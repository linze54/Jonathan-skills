#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_builder.py — 将线性元素序列组装为内容块列表

内容块类型：
  title / meta / body / image / gallery / end
"""


def _should_gallery(images: list) -> bool:
    """
    判断一组连续图片是否应该组成 gallery。
    条件：
    - 2-4 张图片
    - 至少有一张 same_row=True，或全部无独立图注（共享或无图注）
    """
    if len(images) < 2 or len(images) > 4:
        return False
    # 如果有 same_row 标记，直接 gallery
    if any(img.get("same_row") for img in images):
        return True
    # 如果每张图都有各自不同的图注，保持单图
    captions = [img.get("caption") for img in images]
    distinct_captions = [c for c in captions if c]
    if len(distinct_captions) == len(images) and len(set(distinct_captions)) == len(images):
        return False
    return True


def build_structure(elements: list, rel_to_path: dict) -> list:
    """
    将 elements 组装为内容块列表，保留文档顺序。

    rel_to_path: {rel_id → "images/img_NNN.ext"}
    """
    blocks = []
    i = 0
    n = len(elements)

    # 收集 body 段落缓冲区，遇到非 body 时 flush
    body_buffer = []

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
            # 第一个 heading 作为 title，后续作为 body（小标题）
            if not any(b["type"] == "title" for b in blocks):
                blocks.append({"type": "title", "text": elem["text"]})
            else:
                body_buffer.append({"text": elem["text"], "bold": True, "centered": elem.get("centered", False)})
            i += 1

        elif kind == "meta":
            flush_body()
            # 合并连续 meta 行
            meta_lines = [elem["text"]]
            j = i + 1
            while j < n and elements[j]["kind"] in ("meta", "empty"):
                if elements[j]["kind"] == "meta":
                    meta_lines.append(elements[j]["text"])
                j += 1
            blocks.append({"type": "meta", "lines": meta_lines})
            i = j

        elif kind == "body":
            body_buffer.append({"text": elem["text"], "bold": elem.get("bold", False), "centered": elem.get("centered", False)})
            i += 1

        elif kind == "caption_candidate":
            # 未被消费的 caption_candidate 当作 body 处理
            body_buffer.append({"text": elem["text"], "bold": False, "centered": False})
            i += 1

        elif kind == "image":
            flush_body()
            # 收集连续图片（允许中间有 empty）
            img_group = []
            j = i
            while j < n:
                e = elements[j]
                if e["kind"] == "image":
                    src = rel_to_path.get(e.get("rel_id"), "")
                    img_group.append({"src": src, "caption": e.get("caption"), "same_row": e.get("same_row", False)})
                    j += 1
                elif e["kind"] == "empty":
                    # allow one empty between images
                    if j + 1 < n and elements[j + 1]["kind"] == "image":
                        j += 1
                    else:
                        break
                else:
                    break

            if _should_gallery(img_group):
                # shared caption: use first non-None caption
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

    # Append END block
    blocks.append({"type": "end"})

    return blocks
