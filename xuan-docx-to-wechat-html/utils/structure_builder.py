#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_builder.py — 将线性元素序列组装为内容块列表

内容块类型：
  title / body / image / gallery / end
  (meta 元素在此处被丢弃，不进入正文)
"""


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
    """
    将连续图片元素按 para_index 分组，同一 para_index 的图片为同一行。
    每组独立决定是 gallery 还是单图。
    """
    blocks = []
    # 按 para_index 分组
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
            {"src": rel_to_path.get(img.get("rel_id"), ""), "caption": img.get("caption"), "same_row": img.get("same_row", False)}
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
    title_text = None  # 记录标题文本，用于去重

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

        # meta 元素直接丢弃，不进入正文
        if kind == "meta":
            i += 1
            continue

        if kind == "heading":
            flush_body()
            if not any(b["type"] == "title" for b in blocks):
                title_text = elem["text"]
                blocks.append({"type": "title", "text": elem["text"]})
            else:
                body_buffer.append({"text": elem["text"], "bold": True, "centered": elem.get("centered", False)})
            i += 1

        elif kind == "body":
            text = elem["text"]
            # 跳过与标题完全相同的正文段落（标题在正文中的重复）
            if title_text and text.strip() == title_text.strip():
                i += 1
                continue
            body_buffer.append({"text": text, "bold": elem.get("bold", False), "centered": elem.get("centered", False)})
            i += 1

        elif kind == "caption_candidate":
            body_buffer.append({"text": elem["text"], "bold": False, "centered": False})
            i += 1

        elif kind == "image":
            flush_body()
            # 收集连续图片（允许中间有 empty）
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

    flush_body()
    blocks.append({"type": "end"})
    return blocks
