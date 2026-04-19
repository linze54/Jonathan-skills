#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_builder.py — 将线性元素序列组装为内容块列表

内容块类型：
  title / summary / body / image / gallery / end
  (meta 元素在此处被丢弃，不进入正文)

summary 识别规则：
  标题之后、第一张图片之前，连续的"总述性"段落组成 summary 块。
  总述段落特征：包含活动背景/目的/概述关键词，且不是流程叙述。
  流程叙述特征：以"活动伊始"、"随后"、"接着"、"最后"等时序词开头。
"""

import re

_PROCESS_OPENERS = re.compile(
    r"^(活动伊始|活动开始|随后|接着|紧接着|其后|之后|最后|活动最后|活动结束|活动圆满|"
    r"在活动|在本次|在此次|首先|第一|第二|第三|环节|下一|接下来)"
)

_OVERVIEW_SIGNALS = re.compile(
    r"(为深入|为进一步|为贯彻|为落实|为响应|为推进|为加强|为丰富|为提升|"
    r"圆满结束|圆满举行|成功举办|成功举行|顺利举办|顺利举行|"
    r"联合.*举办|联合.*开展|联合.*举行)"
)


def _is_overview_para(text: str) -> bool:
    """判断段落是否为活动总述（背景+目的+概述）。"""
    if _PROCESS_OPENERS.match(text):
        return False
    if _OVERVIEW_SIGNALS.search(text):
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


def _group_images_by_row(img_elements: list, rel_to_path: dict) -> list:
    """按 para_index 分组，同一行的图片组成 gallery，不同行各自独立。"""
    blocks = []
    groups = {}
    order = []
    for img in img_elements:
        pid = img.get("para_index", id(img))
        if pid not in groups:
            groups[pid] = []
            order.append(pid)
        groups[pid].append(img)

    for pid in order:
        group = groups[pid]
        img_data = [
            {
                "src": rel_to_path.get(img.get("rel_id"), ""),
                "caption": img.get("caption"),
                "same_row": img.get("same_row", False),
            }
            for img in group
        ]
        if _should_gallery(img_data):
            shared_caption = next((d["caption"] for d in img_data if d["caption"]), None)
            blocks.append({
                "type": "gallery",
                "images": [{"src": d["src"], "caption": d["caption"]} for d in img_data],
                "shared_caption": shared_caption,
            })
        else:
            for d in img_data:
                blocks.append({"type": "image", "src": d["src"], "caption": d["caption"], "layout": "single_image"})

    return blocks


def build_structure(elements: list, rel_to_path: dict) -> list:
    blocks = []
    i = 0
    n = len(elements)
    body_buffer = []
    title_text = None
    summary_done = False  # 是否已完成 summary 收集
    summary_buffer = []   # 总述段落缓冲

    def flush_body():
        if body_buffer:
            blocks.append({"type": "body", "paragraphs": list(body_buffer)})
            body_buffer.clear()

    def flush_summary():
        nonlocal summary_done
        if summary_buffer:
            blocks.append({"type": "summary", "paragraphs": list(summary_buffer)})
            summary_buffer.clear()
        summary_done = True

    while i < n:
        elem = elements[i]
        kind = elem.get("kind")

        if kind in ("consumed", "empty"):
            i += 1
            continue

        # meta 直接丢弃
        if kind == "meta":
            i += 1
            continue

        if kind == "heading":
            flush_summary()
            flush_body()
            if not any(b["type"] == "title" for b in blocks):
                title_text = elem["text"]
                blocks.append({"type": "title", "text": elem["text"]})
            else:
                body_buffer.append({"text": elem["text"], "bold": True, "centered": elem.get("centered", False)})
            i += 1

        elif kind == "body":
            text = elem["text"]
            # 跳过与标题完全相同的段落
            if title_text and text.strip() == title_text.strip():
                i += 1
                continue

            has_title = any(b["type"] == "title" for b in blocks)

            if has_title and not summary_done:
                # 在标题之后、summary 收集阶段
                if _is_overview_para(text):
                    # 总述段落 → 进入 summary_buffer
                    summary_buffer.append({"text": text, "bold": False, "centered": False})
                else:
                    # 遇到流程叙述或普通段落 → 结束 summary 收集
                    flush_summary()
                    body_buffer.append({"text": text, "bold": elem.get("bold", False), "centered": elem.get("centered", False)})
            else:
                body_buffer.append({"text": text, "bold": elem.get("bold", False), "centered": elem.get("centered", False)})
            i += 1

        elif kind == "caption_candidate":
            body_buffer.append({"text": elem["text"], "bold": False, "centered": False})
            i += 1

        elif kind == "image":
            flush_summary()
            flush_body()
            img_elems = []
            j = i
            while j < n:
                e = elements[j]
                if e["kind"] == "image":
                    img_elems.append(e)
                    j += 1
                elif e["kind"] == "empty":
                    if j + 1 < n and elements[j + 1]["kind"] == "image":
                        j += 1
                    else:
                        break
                else:
                    break

            row_blocks = _group_images_by_row(img_elems, rel_to_path)
            blocks.extend(row_blocks)
            i = j

        else:
            i += 1

    flush_summary()
    flush_body()
    blocks.append({"type": "end"})
    return blocks
