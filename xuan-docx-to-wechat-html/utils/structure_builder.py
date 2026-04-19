#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_builder.py — 将线性元素序列组装为内容块列表

内容块类型：
  title / meta / summary / body / image / gallery / end
"""

import re

_SUMMARY_OPENERS = re.compile(
    r"^(本次|此次|这次|近日|日前|为|为了|经过|通过|在.*[举开进行])"
)
_SUMMARY_KEYWORDS = re.compile(
    r"(活动|圆满|举行|开展|举办|成功|顺利|完成|结束|启动|参与|组织|共.*人|共.*名)"
)


def _is_summary_candidate(para: dict) -> bool:
    """判断段落是否适合作为导语（summary）。"""
    text = para.get("text", "")
    length = len(text)
    if length < 30 or length > 200:
        return False
    if para.get("bold"):
        return False
    # 导语通常以概述性词语开头，或包含活动关键词
    if _SUMMARY_OPENERS.match(text) or _SUMMARY_KEYWORDS.search(text):
        return True
    return False


def _should_gallery(images: list) -> bool:
    if len(images) < 2 or len(images) > 4:
        return False
    if any(img.get("same_row") for img in images):
        return True
    captions = [img.get("caption") for img in images]
    distinct_captions = [c for c in captions if c]
    if len(distinct_captions) == len(images) and len(set(distinct_captions)) == len(images):
        return False
    return True


def build_structure(elements: list, rel_to_path: dict) -> list:
    blocks = []
    i = 0
    n = len(elements)
    body_buffer = []
    has_summary = False

    def flush_body():
        if body_buffer:
            blocks.append({"type": "body", "paragraphs": list(body_buffer)})
            body_buffer.clear()

    while i < n:
        elem = elements[i]
        kind = elem.get("kind")

        if kind in ("consumed", "empty"):
            i += 1
            continue

        if kind == "heading":
            flush_body()
            if not any(b["type"] == "title" for b in blocks):
                blocks.append({"type": "title", "text": elem["text"]})
            else:
                body_buffer.append({"text": elem["text"], "bold": True, "centered": elem.get("centered", False)})
            i += 1

        elif kind == "meta":
            flush_body()
            meta_lines = [elem["text"]]
            j = i + 1
            while j < n and elements[j]["kind"] in ("meta", "empty"):
                if elements[j]["kind"] == "meta":
                    meta_lines.append(elements[j]["text"])
                j += 1
            blocks.append({"type": "meta", "lines": meta_lines})
            i = j

        elif kind == "body":
            # 在 title+meta 之后，第一个符合条件的 body 段落作为 summary
            has_title = any(b["type"] == "title" for b in blocks)
            if has_title and not has_summary and not body_buffer:
                para = {"text": elem["text"], "bold": elem.get("bold", False), "centered": elem.get("centered", False)}
                if _is_summary_candidate(para):
                    flush_body()
                    blocks.append({"type": "summary", "text": elem["text"]})
                    has_summary = True
                    i += 1
                    continue
            body_buffer.append({"text": elem["text"], "bold": elem.get("bold", False), "centered": elem.get("centered", False)})
            i += 1

        elif kind == "caption_candidate":
            body_buffer.append({"text": elem["text"], "bold": False, "centered": False})
            i += 1

        elif kind == "image":
            flush_body()
            img_group = []
            j = i
            while j < n:
                e = elements[j]
                if e["kind"] == "image":
                    src = rel_to_path.get(e.get("rel_id"), "")
                    img_group.append({"src": src, "caption": e.get("caption"), "same_row": e.get("same_row", False)})
                    j += 1
                elif e["kind"] == "empty":
                    if j + 1 < n and elements[j + 1]["kind"] == "image":
                        j += 1
                    else:
                        break
                else:
                    break

            if _should_gallery(img_group):
                shared_caption = next((img["caption"] for img in img_group if img["caption"]), None)
                blocks.append({
                    "type": "gallery",
                    "images": [{"src": img["src"], "caption": img["caption"]} for img in img_group],
                    "shared_caption": shared_caption,
                })
            else:
                for img in img_group:
                    blocks.append({
                        "type": "image",
                        "src": img["src"],
                        "caption": img["caption"],
                        "layout": "single_image",
                    })
            i = j

        else:
            i += 1

    flush_body()
    blocks.append({"type": "end"})
    return blocks
