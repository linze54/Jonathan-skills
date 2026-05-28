#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_extractor.py — 从 docx 中提取内嵌图片到本地目录，支持 Word 图片裁剪
"""

import os
import mimetypes
from PIL import Image


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

# EMF/WMF 等矢量格式无法用 Pillow 裁剪，跳过
_SKIP_CROP_EXTS = {".emf", ".wmf", ".svg"}


def _apply_crop(img: Image.Image, crop: dict) -> Image.Image:
    """根据 Word srcRect 裁剪参数裁切图片。
    crop: {"l": left_1000ths_pct, "r": right_1000ths_pct, "t": top_1000ths_pct, "b": bottom_1000ths_pct}
    值为 0 表示不裁剪，值在 0~100000 之间（千分之一百分比）。
    """
    w, h = img.size
    l_px = int(w * crop["l"] / 100000)
    r_px = w - int(w * crop["r"] / 100000)
    t_px = int(h * crop["t"] / 100000)
    b_px = h - int(h * crop["b"] / 100000)

    # 边界保护
    l_px = max(0, min(l_px, w - 1))
    r_px = max(l_px + 1, min(r_px, w))
    t_px = max(0, min(t_px, h - 1))
    b_px = max(t_px + 1, min(b_px, h))

    return img.crop((l_px, t_px, r_px, b_px))


def extract_images(doc, elements: list, output_dir: str) -> dict:
    """
    根据 elements 中收集到的 rel_id，从 doc 中提取图片到 output_dir/images/。
    如果 element 中包含 crop 信息（Word 截图裁剪），会在提取后自动裁切。

    返回 {rel_id: "images/img_NNN.ext"} 映射。
    未找到的 rel_id 不会出现在返回值中。
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # 收集所有 rel_id（去重，保留顺序）+ 裁剪信息
    seen = set()
    rel_ids_ordered = []
    rel_crop_map = {}  # rel_id -> crop dict
    for elem in elements:
        if elem.get("kind") == "image":
            rid = elem.get("rel_id")
            if rid and rid not in seen:
                seen.add(rid)
                rel_ids_ordered.append(rid)
                crop = elem.get("crop")
                if crop and any(v != 0 for v in crop.values()):
                    rel_crop_map[rid] = crop

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
                ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".bin"
            filename = f"img_{counter:03d}{ext}"
            filepath = os.path.join(images_dir, filename)

            # 获取图片 blob
            blob = part.blob

            # 如果有裁剪信息且格式支持，用 Pillow 裁切
            crop = rel_crop_map.get(rel_id)
            if crop and ext not in _SKIP_CROP_EXTS:
                try:
                    from io import BytesIO
                    img = Image.open(BytesIO(blob))
                    cropped = _apply_crop(img, crop)
                    # 保存裁剪后的图片
                    if cropped.mode in ("RGBA", "P") and ext == ".jpg":
                        cropped = cropped.convert("RGB")
                    cropped.save(filepath)
                except Exception:
                    # 裁剪失败则回退到原始图片
                    with open(filepath, "wb") as f:
                        f.write(blob)
            else:
                with open(filepath, "wb") as f:
                    f.write(blob)

            rel_to_path[rel_id] = f"images/{filename}"
            counter += 1
        except Exception:
            pass

    return rel_to_path
