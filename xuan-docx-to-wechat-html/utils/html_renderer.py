#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_renderer.py — 将内容块渲染为微信公众号兼容的 HTML 正文片段
v2: 移除 flex/grid，嵌套≤3层，图片 display:block;width:100%
输出是正文片段（无 html/head/body），直接提交微信草稿箱接口。
"""

import html as html_lib


def _esc(text: str) -> str:
    return html_lib.escape(str(text or ""), quote=False)


def render_html(blocks: list, style: dict) -> str:
    parts = []
    s = style

    # 外层容器（1层）
    parts.append(f'<section style="{s["wrap"]}">')

    for block in blocks:
        btype = block.get("type")

        if btype == "title":
            # 层级：section > div > p（3层）
            parts.append(
                f'<div style="{s["title_wrap"]}">'
                f'<p style="{s["title"]}">{_esc(block["text"])}</p>'
                f'</div>'
            )

        elif btype == "meta":
            lines_html = "".join(
                f'<span style="{s["meta_line"]}">{_esc(line)}</span><br />'
                for line in block.get("lines", [])
            )
            parts.append(f'<div style="{s["meta_wrap"]}">{lines_html}</div>')

        elif btype == "summary":
            paras = block.get("paragraphs", [])
            if not paras:
                continue
            # 层级：section > div > p（3层）
            inner = "".join(
                f'<p style="{s["summary_text"]}">{_esc(p["text"])}</p>'
                for p in paras
            )
            parts.append(f'<div style="{s["summary_block"]}">{inner}</div>')

        elif btype == "body":
            paras = block.get("paragraphs", [])
            if not paras:
                continue
            inner = ""
            for p in paras:
                text = _esc(p["text"])
                if p.get("bold"):
                    inner += f'<p style="{s["body_bold"]}">{text}</p>'
                elif p.get("centered"):
                    inner += f'<p style="{s["body_centered"]}">{text}</p>'
                else:
                    inner += f'<p style="{s["body_para"]}">{text}</p>'
            parts.append(f'<div style="{s["body_block"]}">{inner}</div>')

        elif btype == "image":
            # 层级：section > div > img（3层）
            src = _esc(block.get("src", ""))
            caption = block.get("caption")
            cap_html = ""
            if caption:
                cap_html = f'<p style="{s["caption"]}">{_esc(caption)}</p>'
            parts.append(
                f'<div style="{s["image_block"]}">'
                f'<img src="{src}" data-local-src="{src}" style="{s["image"]}" />'
                f'{cap_html}'
                f'</div>'
            )

        elif btype == "gallery":
            images = block.get("images", [])
            shared_caption = block.get("shared_caption")
            if not images:
                continue

            # 双图并排：inline-block 方案，每行2张，超出自动换行
            # 层级：section > div > span > img（4层，但 span 是行内元素，微信可接受）
            imgs_html = ""
            for idx, img in enumerate(images):
                src = _esc(img.get("src", ""))
                cap = img.get("caption")
                item_style = s["gallery_item_first"] if idx % 2 == 0 else s["gallery_item_rest"]
                cap_html = ""
                if cap and cap != shared_caption:
                    cap_html = f'<p style="{s["caption"]}">{_esc(cap)}</p>'
                imgs_html += (
                    f'<span style="{item_style}">'
                    f'<img src="{src}" data-local-src="{src}" style="{s["gallery_image"]}" />'
                    f'{cap_html}'
                    f'</span>'
                )

            shared_cap_html = ""
            if shared_caption:
                shared_cap_html = f'<p style="{s["caption"]}">{_esc(shared_caption)}</p>'

            parts.append(
                f'<div style="{s["gallery_row"]}">'
                f'{imgs_html}'
                f'</div>'
                f'{shared_cap_html}'
            )

        elif btype == "end":
            parts.append(
                f'<div style="{s["end_block"]}">'
                f'<span style="{s["end_text"]}">— END —</span>'
                f'</div>'
            )

    parts.append("</section>")
    return "\n".join(parts)
