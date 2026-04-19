#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_renderer.py — 将内容块渲染为微信兼容的 HTML 片段

输出是文章正文片段，不是完整网页（无 html/head/body 标签）。
所有样式内联，不依赖外链 CSS，不使用 JS。
"""

import html as html_lib


def _esc(text: str) -> str:
    return html_lib.escape(str(text or ""), quote=False)


def render_html(blocks: list, style: dict) -> str:
    """
    blocks: structure_builder 输出的内容块列表
    style: community_wechat_brief_style.get_styles() 返回的样式字典
    返回 HTML 字符串（文章片段）。
    """
    parts = []
    s = style

    parts.append(f'<section style="{s["wrap"]}">')

    for block in blocks:
        btype = block.get("type")

        if btype == "title":
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
            src = _esc(block.get("src", ""))
            caption = block.get("caption")
            img_tag = (
                f'<img src="{src}" data-local-src="{src}" '
                f'style="{s["image"]}" />'
            )
            cap_html = ""
            if caption:
                cap_html = f'<p style="{s["caption"]}">{_esc(caption)}</p>'
            parts.append(
                f'<div style="{s["image_block"]}">'
                f'{img_tag}{cap_html}'
                f'</div>'
            )

        elif btype == "gallery":
            images = block.get("images", [])
            shared_caption = block.get("shared_caption")
            imgs_html = ""
            for img in images:
                src = _esc(img.get("src", ""))
                cap = img.get("caption")
                cap_html = f'<p style="{s["caption"]}">{_esc(cap)}</p>' if cap and cap != shared_caption else ""
                imgs_html += (
                    f'<div style="{s["gallery_item"]}">'
                    f'<img src="{src}" data-local-src="{src}" style="{s["gallery_image"]}" />'
                    f'{cap_html}'
                    f'</div>'
                )
            shared_cap_html = ""
            if shared_caption:
                shared_cap_html = f'<p style="{s["caption"]}">{_esc(shared_caption)}</p>'
            parts.append(
                f'<div style="{s["gallery_block"]}">'
                f'<div style="{s["gallery_row"]}">{imgs_html}</div>'
                f'{shared_cap_html}'
                f'</div>'
            )

        elif btype == "end":
            parts.append(
                f'<div style="{s["end_block"]}">'
                f'<span style="{s["end_text"]}">— END —</span>'
                f'</div>'
            )

    parts.append("</section>")
    return "\n".join(parts)
