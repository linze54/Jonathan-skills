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
    for b in blocks:
        if b["type"] == "title":
            return b["text"]
    return ""


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
        html_content = render_html(blocks, style)

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

        result = {
            "status": "success",
            "input_file": input_file,
            "output_html": output_html,
            "output_images_dir": os.path.join(output_dir, "images"),
            "output_json": output_json,
            "title": _find_title(blocks),
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
