#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parser.py — 按文档 XML 顺序构建统一线性元素序列
"""

import re
from lxml import etree
from docx import Document
from docx.oxml.ns import qn

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"

_BODY_OPENERS = re.compile(
    r"^(本次|活动|通过|为了|经过|此次|这次|在.*[举开进行]|参与|组织|开展|共有|共计|全体|各位)"
)
_SECTION_HEADER = re.compile(r"[：:]$")
_DATE_PATTERN = re.compile(r"\d{4}[年/-]\d{1,2}[月/-]\d{1,2}")
_ORG_PATTERN = re.compile(r"(社区|街道|委员会|志愿|协会|中心|办事处|党委|居委|服务中心|工作中心)")
_EYEBROW_WORDS = re.compile(
    r"^(活动简报|工作简报|社区简报|活动通讯|工作通讯|简报|通讯|公告|通知|新闻|资讯|动态|快讯|特刊|专刊|第.{1,4}期)$"
)


def _get_text(para_elem) -> str:
    parts = []
    for r in para_elem.iter(qn("w:t")):
        t = r.text or ""
        parts.append(t)
    return "".join(parts).strip()


def _is_bold(para_elem) -> bool:
    for r in para_elem.iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is not None and rpr.find(qn("w:b")) is not None:
            return True
        if r.find(qn("w:t")) is not None:
            return False
    return False


def _is_centered(para_elem) -> bool:
    ppr = para_elem.find(qn("w:pPr"))
    if ppr is None:
        return False
    jc = ppr.find(qn("w:jc"))
    if jc is None:
        return False
    return jc.get(qn("w:val"), "") in ("center", "both")


def _get_style_name(para_elem, doc) -> str:
    ppr = para_elem.find(qn("w:pPr"))
    if ppr is None:
        return ""
    pstyle = ppr.find(qn("w:pStyle"))
    if pstyle is None:
        return ""
    style_id = pstyle.get(qn("w:val"), "")
    try:
        style = doc.styles.get_by_id(style_id, 1)
        return style.name.lower() if style else style_id.lower()
    except Exception:
        return style_id.lower()


def _extract_images_from_para(para_elem):
    images = []
    for blip in para_elem.iter("{%s}blip" % NS_A):
        rel_id = blip.get("{%s}embed" % NS_R) or blip.get("{%s}link" % NS_R)
        if not rel_id:
            continue
        width_emu = height_emu = 0
        parent = blip.getparent()
        while parent is not None:
            extent = parent.find("{%s}extent" % NS_WP)
            if extent is not None:
                width_emu = int(extent.get("cx", 0))
                height_emu = int(extent.get("cy", 0))
                break
            parent = parent.getparent()
        # 读取 Word 中图片的裁剪信息 (srcRect)
        crop = None
        blipFill = blip.getparent()
        if blipFill is not None:
            srcRect = blipFill.find("{%s}srcRect" % NS_A)
            if srcRect is not None:
                crop = {
                    "l": int(srcRect.get("l", 0)),
                    "r": int(srcRect.get("r", 0)),
                    "t": int(srcRect.get("t", 0)),
                    "b": int(srcRect.get("b", 0)),
                }
        images.append({"rel_id": rel_id, "width_emu": width_emu, "height_emu": height_emu, "crop": crop})
    same_row = len(images) > 1
    for img in images:
        img["same_row"] = same_row
    return images


def _classify_text_para(text, para_elem, doc, para_index) -> dict:
    if not text:
        return {"kind": "empty"}

    style_name = _get_style_name(para_elem, doc)
    centered = _is_centered(para_elem)
    bold = _is_bold(para_elem)
    length = len(text)

    if "heading" in style_name or "标题" in style_name:
        level = 1
        for i in range(1, 7):
            if str(i) in style_name:
                level = i
                break
        if _EYEBROW_WORDS.match(text):
            return {"kind": "meta", "text": text}
        return {"kind": "heading", "text": text, "level": level, "bold": bold, "centered": centered}

    if centered and bold and length <= 30 and para_index < 10:
        if _EYEBROW_WORDS.match(text):
            return {"kind": "meta", "text": text}
        return {"kind": "heading", "text": text, "level": 2, "bold": True, "centered": centered}

    # 机构名+日期组合，短文本视为 meta（长文本可能是包含日期的正文导语）
    if _DATE_PATTERN.search(text) and _ORG_PATTERN.search(text) and length <= 80:
        return {"kind": "meta", "text": text}

    # 早期居中段落：日期、机构名、或极短文本
    # 但排除可能是图注的文本
    caption_keywords = ["进行", "介绍", "现场", "打卡", "留念", "拍照", "展示", "创作", "绘制", "手绘"]
    has_caption_keyword = any(keyword in text for keyword in caption_keywords)
    
    if para_index < 8 and centered and (
        _DATE_PATTERN.search(text) or _ORG_PATTERN.search(text) or length <= 20
    ) and not has_caption_keyword and length <= 80:
        return {"kind": "meta", "text": text}

    # 图注识别优先：包含图注关键词的短文本
    caption_keywords = ["进行", "介绍", "现场", "打卡", "留念", "拍照", "展示", "创作", "绘制", "手绘"]
    has_caption_keyword = any(keyword in text for keyword in caption_keywords)
    
    if has_caption_keyword and length <= 30 and para_index > 3:
        return {"kind": "caption_candidate", "text": text, "para_index": para_index}
    
    # 活动标题识别：更精确的识别规则
    # 真正的活动标题通常包含"活动"且以"圆满结束"、"成功举办"等结尾
    # 排除包含"介绍了"、"讲解了"等动词的正文内容
    title_indicators = ["圆满结束", "成功举办", "顺利开展", "正式启动", "拉开帷幕"]
    body_indicators = ["介绍了", "讲解了", "表示", "强调", "指出", "认为"]
    
    is_likely_title = (
        "活动" in text 
        and 10 <= length <= 100 
        and para_index < 10
        and any(indicator in text for indicator in title_indicators)
        and not any(indicator in text for indicator in body_indicators)
    )
    
    if is_likely_title:
        return {"kind": "meta", "text": text}
    
    # Caption candidate - 基本版
    is_caption_candidate = (
        length <= 50
        and not bold
        and not _BODY_OPENERS.match(text)
        and not _SECTION_HEADER.search(text)
        and not _DATE_PATTERN.search(text)
        and text.count("。") + text.count("！") + text.count("？") == 0
    )
    
    if is_caption_candidate:
        return {"kind": "caption_candidate", "text": text, "para_index": para_index}

    return {"kind": "body", "text": text, "bold": bold, "centered": centered}


def _extract_table_elements(tbl_elem, doc, para_index_start: int):
    """
    提取表格中的图片和文字，每行独立编号。
    同行图片标记 same_row=True；单元格内图片下方的文字作为该图片的 caption。
    """
    elements = []
    para_index = para_index_start

    for row in tbl_elem.iter(qn("w:tr")):
        row_images = []
        row_texts = []

        for cell in row.iter(qn("w:tc")):
            cell_imgs = _extract_images_from_para(cell)
            cell_text = " ".join(
                t.text or "" for t in cell.iter(qn("w:t"))
            ).strip()

            if cell_imgs:
                # 单元格内同时有图片和文字：文字作为该图片的 caption
                caption = cell_text if cell_text else None
                for img in cell_imgs:
                    img["cell_caption"] = caption
                row_images.extend(cell_imgs)
            elif cell_text:
                row_texts.append(cell_text)

        if row_images:
            same_row = len(row_images) > 1
            for img in row_images:
                img["kind"] = "image"
                img["para_index"] = para_index
                img["same_row"] = same_row
                # cell_caption 优先作为图注
                if img.get("cell_caption"):
                    img["caption"] = img.pop("cell_caption")
                else:
                    img.pop("cell_caption", None)
                elements.append(img)
        elif row_texts:
            combined = "　".join(row_texts)
            elements.append({"kind": "body", "text": combined, "bold": False, "centered": False})

        para_index += 1

    return elements, para_index


def parse_document(doc_path: str) -> list:
    doc = Document(doc_path)
    elements = []
    para_index = 0

    body = doc.element.body
    for child in body:
        try:
            local = etree.QName(child.tag).localname
        except Exception:
            continue

        if local == "p":
            para_elem = child
            images = _extract_images_from_para(para_elem)
            text = _get_text(para_elem)

            if images and text:
                text_elem = _classify_text_para(text, para_elem, doc, para_index)
                elements.append(text_elem)
                for img in images:
                    img["kind"] = "image"
                    img["para_index"] = para_index
                    elements.append(img)
            elif images:
                for img in images:
                    img["kind"] = "image"
                    img["para_index"] = para_index
                    elements.append(img)
            else:
                elem = _classify_text_para(text, para_elem, doc, para_index)
                elements.append(elem)

            para_index += 1

        elif local == "tbl":
            tbl_elements, para_index = _extract_table_elements(child, doc, para_index)
            elements.extend(tbl_elements)

    return elements
