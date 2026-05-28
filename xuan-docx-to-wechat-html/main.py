#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — xuan-docx-to-wechat-html 入口

用法：
  python main.py --input /path/to/article.docx --output-dir /path/to/output
  python main.py --input /path/to/article.docx --output-dir /path/to/output --debug
"""

import argparse
import json
import os
import sys

# 支持从任意工作目录调用
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SKILL_DIR)

from utils.parser import parse_document
from utils.image_extractor import extract_images
from utils.caption_matcher import match_captions
from utils.structure_builder import build_structure
from utils.html_renderer import render_html
from docx import Document


_STYLES = {
    "community_wechat_brief_style": "templates.community_wechat_brief_style",
}


def _load_style(style_name: str) -> dict:
    module_path = _STYLES.get(style_name)
    if not module_path:
        raise ValueError(f"Unknown style: {style_name}. Available: {list(_STYLES.keys())}")
    import importlib
    mod = importlib.import_module(module_path)
    return mod.get_styles()


def _find_title(blocks: list) -> str:
    """查找文档标题（兼容旧版本）"""
    for b in blocks:
        if b["type"] == "title":
            return b["text"]
    return ""


def _extract_document_info(blocks: list) -> dict:
    """提取文档信息
    
    从文档中提取以下信息：
    1. 文档类型（如"活 动 简 报"）
    2. 作者/机构信息（如"成都同德社会工作服务中心 2026年4月18日"）
    3. 真正的推文标题（如"长林盘社区'公益一把伞·共治暖人心'共享雨伞创作活动圆满结束"）
    
    返回格式：
    {
        "doc_type": "活 动 简 报",
        "author_info": "成都同德社会工作服务中心 2026年4月18日",
        "article_title": "长林盘社区'公益一把伞·共治暖人心'共享雨伞创作活动圆满结束"
    }
    """
    # 查找type=="meta"的块
    meta_texts = []
    for b in blocks:
        if b["type"] == "meta":
            text = b.get("text", "").strip()
            if text:
                meta_texts.append(text)
    
    # 过滤掉图注等非标题meta
    filtered_meta_texts = []
    for text in meta_texts:
        # 跳过可能是图注的文本
        if any(word in text for word in ["进行", "介绍", "现场", "打卡", "留念", "主持人", "拍照"]):
            continue
        filtered_meta_texts.append(text)
    
    result = {
        "doc_type": "",
        "author_info": "",
        "article_title": ""
    }
    
    if not filtered_meta_texts:
        return result
    
    # 分析meta文本
    for i, text in enumerate(filtered_meta_texts):
        # 先判断是否为文档类型（检查去除空格后的文本）
        text_no_space = text.replace(" ", "")
        if "简报" in text_no_space or "报告" in text_no_space or "总结" in text_no_space:
            result["doc_type"] = text
            continue
        
        # 判断是否为作者/机构信息
        if ("中心" in text or "公司" in text or "工作室" in text or 
            ("年" in text and "月" in text)):
            result["author_info"] = text
            continue
        
        # 判断是否为活动标题
        if ("社区" in text and "活动" in text) or ("公益" in text and "活动" in text):
            result["article_title"] = text
            continue
        
        # 如果还没有找到活动标题，且文本包含"活动"
        if not result["article_title"] and "活动" in text:
            result["article_title"] = text
    
    return result


def _find_article_title(blocks: list) -> str:
    """识别真正的推文标题（用于HTML渲染）
    
    只返回真正的推文标题，不包含文档类型和作者信息
    """
    doc_info = _extract_document_info(blocks)
    return doc_info.get("article_title", "")


def _find_summary_candidate(blocks: list) -> str:
    for b in blocks:
        if b["type"] == "body":
            paras = b.get("paragraphs", [])
            for p in paras:
                text = p.get("text", "").strip()
                if len(text) > 10:
                    return text[:120]
    return ""


def _find_first_image(blocks: list) -> str:
    for b in blocks:
        if b["type"] == "image":
            return b.get("src", "")
        if b["type"] == "gallery":
            imgs = b.get("images", [])
            if imgs:
                return imgs[0].get("src", "")
    return ""


def _count_images(blocks: list) -> int:
    count = 0
    for b in blocks:
        if b["type"] == "image":
            count += 1
        elif b["type"] == "gallery":
            count += len(b.get("images", []))
    return count


def _count_captions(blocks: list) -> int:
    count = 0
    for b in blocks:
        if b["type"] == "image" and b.get("caption"):
            count += 1
        elif b["type"] == "gallery":
            for img in b.get("images", []):
                if img.get("caption"):
                    count += 1
            if b.get("shared_caption"):
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Convert .docx to WeChat-compatible HTML")
    parser.add_argument("--input", required=True, help=".docx 文件路径")
    parser.add_argument("--output-dir", default=None, help="输出目录（默认：docx 同目录下的 output/）")
    parser.add_argument("--style", default="community_wechat_brief_style", help="渲染风格名称")
    parser.add_argument("--debug", action="store_true", help="输出 parsed.json 中间结构")
    parser.add_argument("--keep-original-text", action="store_true", default=True, help="保留原文措辞（默认开启）")
    args = parser.parse_args()

    input_file = os.path.abspath(args.input)
    if not os.path.exists(input_file):
        print(json.dumps({"status": "error", "error": f"File not found: {input_file}"}, ensure_ascii=False))
        sys.exit(1)

    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(os.path.dirname(input_file), "output")

    os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. 解析文档
        elements = parse_document(input_file)

        # 2. 提取图片
        doc = Document(input_file)
        rel_to_path = extract_images(doc, elements, output_dir)

        # 3. 绑定图注
        elements = match_captions(elements)

        # 4. 构建结构
        blocks = build_structure(elements, rel_to_path)

        # 5. 渲染 HTML
        style = _load_style(args.style)
        doc_info = _extract_document_info(blocks)
        article_title = doc_info.get("article_title", "")
        author_info = doc_info.get("author_info", "")
        html_content = render_html(blocks, style, article_title, author_info)

        # 6. 写出文件
        output_html = os.path.join(output_dir, "article_wechat.html")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        output_json = None
        if args.debug:
            output_json = os.path.join(output_dir, "parsed.json")
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(
                    {"elements": elements, "blocks": blocks},
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )

        # 提取文档信息
        doc_info = _extract_document_info(blocks)
        article_title = _find_article_title(blocks)
        
        result = {
            "status": "success",
            "input_file": input_file,
            "output_html": output_html,
            "output_images_dir": os.path.join(output_dir, "images"),
            "output_json": output_json,
            "title": _find_title(blocks),
            "article_title": article_title,  # 真正的推文标题（用于HTML渲染）
            "doc_type": doc_info.get("doc_type", ""),  # 文档类型
            "author_info": doc_info.get("author_info", ""),  # 作者/机构信息
            "summary_candidate": _find_summary_candidate(blocks),
            "first_image_candidate": _find_first_image(blocks),
            "images_count": _count_images(blocks),
            "captions_count": _count_captions(blocks),
            "style_name": args.style,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
