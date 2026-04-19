#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_extractor.py — 从 docx 中提取内嵌图片到本地目录
"""

import os
import mimetypes


_CONTENT_TYPE_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
    "image/svg+xml": ".svg",
    "image/x-emf": ".emf",
    "image/x-wmf": ".wmf",
}


def extract_images(doc, elements: list, output_dir: str) -> dict:
    """
    根据 elements 中收集到的 rel_id，从 doc 中提取图片到 output_dir/images/。

    返回 {rel_id: "images/img_NNN.ext"} 映射。
    未找到的 rel_id 不会出现在返回值中。
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # 收集所有 rel_id（去重，保留顺序）
    seen = set()
    rel_ids_ordered = []
    for elem in elements:
        if elem.get("kind") == "image":
            rid = elem.get("rel_id")
            if rid and rid not in seen:
                seen.add(rid)
                rel_ids_ordered.append(rid)

    rel_to_path = {}
    counter = 1

    for rel_id in rel_ids_ordered:
        try:
            part = doc.part.related_parts.get(rel_id)
            if part is None:
                continue
            content_type = part.content_type or ""
            ext = _CONTENT_TYPE_EXT.get(content_type)
            if ext is None:
                # fallback: guess from content_type
                ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".bin"
            filename = f"img_{counter:03d}{ext}"
            filepath = os.path.join(images_dir, filename)
            with open(filepath, "wb") as f:
                f.write(part.blob)
            rel_to_path[rel_id] = f"images/{filename}"
            counter += 1
        except Exception as e:
            # skip unreadable images silently
            pass

    return rel_to_path
