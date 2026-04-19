#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parser.py — 按文档 XML 顺序构建统一线性元素序列

每个元素是一个 dict，kind 字段为：
  heading / meta / body / image / caption_candidate / empty
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
_ORG_PATTERN = re.compile(r"(社区|街道|委员会|志愿|协会|中心|办事处|党委|居委)")

# 眉题/栏目标识词：短小居中加粗，但不是真正的文章标题
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
        images.append({"rel_id": rel_id, "width_emu": width_emu, "height_emu": height_emu})

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

    # Heading: style name
    if "heading" in style_name or "标题" in style_name:
        level = 1
        for i in range(1, 7):
            if str(i) in style_name:
                level = i
                break
        # 眉题用 heading 样式但内容是分类词 → 降级为 meta
        if _EYEBROW_WORDS.match(text):
            return {"kind": "meta", "text": text}
        return {"kind": "heading", "text": text, "level": level, "bold": bold, "centered": centered}

    # centered + bold + short → heading candidate，但眉题降级为 meta
    if centered and bold and length <= 30 and para_index < 10:
        if _EYEBROW_WORDS.match(text):
            return {"kind": "meta", "text": text}
        return {"kind": "heading", "text": text, "level": 2, "bold": True, "centered": centered}

    # Meta: early paragraphs, centered, with date/org or very short
    if para_index < 8 and centered and (
        _DATE_PATTERN.search(text) or _ORG_PATTERN.search(text) or length <= 20
    ):
        return {"kind": "meta", "text": text}

    # Caption candidate: short, no bold, no body-opener, no mid-sentence punctuation
    if (
        length <= 40
        and not bold
        and not _BODY_OPENERS.match(text)
        and not _SECTION_HEADER.search(text)
        and not _DATE_PATTERN.search(text)
        and text.count("。") + text.count("！") + text.count("？") == 0
    ):
        return {"kind": "caption_candidate", "text": text, "para_index": para_index}

    return {"kind": "body", "text": text, "bold": bold, "centered": centered}


def _extract_table_elements(tbl_elem, para_index):
    """
    提取表格中的图片和文字。
    Word 中"两图一行"通常用 2 列表格实现。
    同一行的多张图片标记 same_row=True。
    """
    elements = []
    for row in tbl_elem.iter(qn("w:tr")):
        row_images = []
        row_texts = []
        for cell in row.iter(qn("w:tc")):
            # 提取单元格内图片
            cell_imgs = _extract_images_from_para(cell)
            # 提取单元格内文字（跨所有段落）
            cell_text = " ".join(
                t.text or "" for t in cell.iter(qn("w:t"))
            ).strip()
            if cell_imgs:
                row_images.extend(cell_imgs)
            elif cell_text:
                row_texts.append(cell_text)

        if row_images:
            # 同一行多图 → same_row=True
            same_row = len(row_images) > 1
            for img in row_images:
                img["kind"] = "image"
                img["para_index"] = para_index
                img["same_row"] = same_row
                elements.append(img)
        elif row_texts:
            combined = "　".join(row_texts)
            elements.append({"kind": "body", "text": combined, "bold": False, "centered": False})

    return elements


def parse_document(doc_path: str) -> list:
    """
    按 XML 顺序构建统一线性元素序列。
    返回 list of dict，每个 dict 包含 kind 字段。
    """
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
            tbl_elements = _extract_table_elements(child, para_index)
            elements.extend(tbl_elements)
            para_index += 1

    return elements
