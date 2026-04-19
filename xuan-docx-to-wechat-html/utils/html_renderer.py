#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_renderer.py — 将内容块渲染为完整 HTML 页面（微信公众号兼容）

输出是完整 HTML 页面，所有样式内联，不依赖外链 CSS，不使用 JS。
"""

import html as html_lib


def _esc(text: str) -> str:
    return html_lib.escape(str(text or ""), quote=False)


_HTML_HEAD = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;">
"""

_HTML_FOOT = """\
</body>
</html>"""


def render_html(blocks: list, style: dict) -> str:
    """
    blocks: structure_builder 输出的内容块列表
    style: community_wechat_brief_style.get_styles() 返回的样式字典
    返回完整 HTML 页面字符串。
    """
    s = style

    # 提取标题用于 <title>
    page_title = ""
    for b in blocks:
        if b.get("type") == "title":
            page_title = b.get("text", "")
            break

    parts = [_HTML_HEAD.format(title=_esc(page_title or "文章"))]
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
            parts.append(
                f'<div style="{s["summary_block"]}">'
                f'<p style="{s["summary_text"]}">{_esc(block["text"])}</p>'
                f'</div>'
            )

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
                f'<span style="{s["end_star"]}">★ </span>'
                f'<span style="{s["end_text"]}">END</span>'
                f'<span style="{s["end_star"]}"> ★</span>'
                f'</div>'
            )

    parts.append("</section>")
    parts.append(_HTML_FOOT)
    return "\n".join(parts)
