#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
community_wechat_brief_style.py — 社区活动简报风格

低饱和暖色系，微信公众号图文风格，内联样式。
"""


def get_styles() -> dict:
    return {
        # 外层容器
        "wrap": (
            "max-width:680px;"
            "margin:0 auto;"
            "padding:16px 12px 32px 12px;"
            "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
            "background:#ffffff;"
            "color:#3d3530;"
        ),

        # 标题区
        "title_wrap": (
            "text-align:center;"
            "padding:28px 8px 12px 8px;"
        ),
        "title": (
            "font-size:22px;"
            "font-weight:bold;"
            "color:#1a1a1a;"
            "line-height:1.6;"
            "margin:0 0 8px 0;"
            "letter-spacing:1px;"
        ),

        # 元信息区
        "meta_wrap": (
            "text-align:center;"
            "padding:4px 8px 20px 8px;"
            "border-bottom:1px solid #eeeeee;"
            "margin-bottom:20px;"
        ),
        "meta_line": (
            "font-size:13px;"
            "color:#aaaaaa;"
            "line-height:2;"
        ),

        # 导语卡片
        "summary_block": (
            "background:#fff9f0;"
            "border-left:4px solid #c0392b;"
            "border-radius:0 4px 4px 0;"
            "padding:14px 16px;"
            "margin-bottom:20px;"
        ),
        "summary_text": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "margin:0;"
            "font-style:italic;"
        ),

        # 正文块（白底，无边框卡片）
        "body_block": (
            "background:#ffffff;"
            "padding:0 4px;"
            "margin-bottom:12px;"
        ),
        "body_para": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "margin:0 0 12px 0;"
            "text-indent:2em;"
        ),
        "body_bold": (
            "font-size:16px;"
            "line-height:1.8;"
            "color:#1a1a1a;"
            "font-weight:bold;"
            "margin:16px 0 8px 0;"
            "text-indent:0;"
        ),
        "body_centered": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "text-align:center;"
            "margin:0 0 8px 0;"
        ),

        # 单图块
        "image_block": (
            "text-align:center;"
            "margin:20px 0;"
            "padding:0;"
        ),
        "image": (
            "display:inline-block;"
            "max-width:100%;"
            "border-radius:4px;"
            "vertical-align:top;"
        ),

        # 图注
        "caption": (
            "font-size:12px;"
            "color:#aaaaaa;"
            "text-align:center;"
            "margin:6px 0 0 0;"
            "line-height:1.6;"
        ),

        # 宫格图块（双图并排）
        "gallery_block": (
            "margin:20px 0;"
            "padding:0;"
        ),
        "gallery_row": (
            "display:flex;"
            "flex-wrap:wrap;"
            "gap:8px;"
            "justify-content:center;"
        ),
        "gallery_item": (
            "flex:1 1 45%;"
            "max-width:48%;"
            "text-align:center;"
        ),
        "gallery_image": (
            "display:block;"
            "width:100%;"
            "border-radius:4px;"
        ),

        # 文末收束区（红底白字）
        "end_block": (
            "text-align:center;"
            "padding:18px 0 18px 0;"
            "margin-top:32px;"
            "background:#c0392b;"
            "border-radius:4px;"
        ),
        "end_text": (
            "font-size:14px;"
            "color:#ffffff;"
            "letter-spacing:4px;"
            "font-weight:bold;"
        ),
        "end_star": (
            "font-size:14px;"
            "color:#f1c40f;"
            "letter-spacing:2px;"
        ),
    }
