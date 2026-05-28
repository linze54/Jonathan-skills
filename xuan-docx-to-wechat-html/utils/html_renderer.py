#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_renderer.py - 将内容块渲染为微信公众号兼容的 HTML 正文片段
v2: 移除 flex/grid,嵌套≤3层,图片 display:block;width:100%
输出是正文片段(无 html/head/body),直接提交微信草稿箱接口。
"""

import html as html_lib
import re


def _esc(text: str) -> str:
    return html_lib.escape(str(text or ""), quote=False)


def _extract_author_from_info(author_info: str) -> str:
    """从作者信息中提取机构名称

    示例:
    输入: "成都同德社会工作服务中心                2026年4月18日"
    输出: "同德社工中心" (微信限制16字符,需要缩短)
    """
    if not author_info:
        return ""

    # 移除日期部分(匹配 年 月 日 模式)
    date_pattern = r'\s*\d{4}[年\-\.]\d{1,2}[月\-\.]\d{1,2}[日]?\s*'
    text_without_date = re.sub(date_pattern, '', author_info)

    # 提取机构名称
    author = text_without_date.strip()

    # 微信限制作者名称最多16个字符,这里我们生成更短的版本
    if "成都同德社会工作服务中心" in author:
        return "同德社工中心"  # 8个字符
    elif "同德社会工作服务中心" in author:
        return "同德社工中心"  # 8个字符
    elif "同德社工中心" in author:
        return "同德社工中心"  # 8个字符

    # 其他机构名称的简化规则
    if "中心" in author:
        parts = author.split("中心")
        if len(parts) > 1:
            base = parts[0]
            # 如果基础名称太长,进一步简化
            if len(base) > 10:
                # 取最后几个字
                base = base[-6:] if len(base) > 6 else base
            return base + "中心"

    # 如果还是太长,直接截断到12个字符(留一些余量)
    if len(author) > 12:
        author = author[:12]

    return author


def render_html(blocks: list, style: dict, article_title: str = "", author_info: str = "") -> str:
    """将内容块渲染为微信公众号兼容的 HTML 正文片段

    Args:
        blocks: 内容块列表
        style: 样式配置字典
        article_title: 推文标题(可选)
        author_info: 作者信息(可选)
    """
    parts = []
    s = style

    # 外层容器(1层)
    parts.append(f'<section style="{s["wrap"]}">')

    # 添加推文信息备注(不渲染到页面,仅供baoyu-skill读取)
    if article_title or author_info:
        remarks = []
        if article_title:
            remarks.append(f'<!-- ARTICLE_TITLE: {_esc(article_title)} -->')
        if author_info:
            # 从作者信息中提取机构名称
            author = _extract_author_from_info(author_info)
            if author:
                remarks.append(f'<!-- ARTICLE_AUTHOR: {_esc(author)} -->')
        if remarks:
            parts.append('\n'.join(remarks))

    for block in blocks:
        btype = block.get("type")

        if btype == "title":
            # 标题不渲染到正文中，因为微信推文标题通过API的title字段已经展示
            # 避免标题重复显示
            continue

        elif btype == "meta":
            # meta信息（文档类型、机构名、日期等）不渲染到正文中
            # 这些信息通过API的元数据字段传递，避免与推文标题重复
            continue

        elif btype == "preamble":
            # 前言/副标题/项目名称不渲染到正文中
            # 这些内容与推文标题重复，已通过API的title字段展示
            continue

        elif btype == "summary":
            paras = block.get("paragraphs", [])
            if not paras:
                continue
            # 双层边框效果：外层红色实线 + 内层红色虚线
            inner = "".join(
                f'<p style="{s["summary_text"]}">{_esc(p["text"])}</p>'
                for p in paras
            )
            parts.append(
                f'<div style="{s["summary_outer"]}">'
                f'<div style="{s["summary_inner"]}">'
                f'{inner}'
                f'</div>'
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
            # 层级:section > div > img(3层)
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

            # 双图并排:inline-block 方案,每行2张,超出自动换行
            # 层级:section > div > span > img(4层,但 span 是行内元素,微信可接受)
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
                f'<span style="{s["end_text"]}">- END -</span>'
                f'</div>'
            )

    parts.append("</section>")
    return "\n".join(parts)
