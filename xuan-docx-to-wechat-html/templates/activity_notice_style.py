#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
activity_notice_style.py — 社区活动通知风格

微信公众号兼容优先：只使用内联样式、普通 div/table/p/img，不使用
flex、grid、外链 CSS、脚本、复杂定位或背景图。
"""


def get_styles() -> dict:
    return {
        "wrap": (
            "margin:0 auto;"
            "padding:16px 12px;"
            "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
            "background:#fffdf8;"
            "color:#2f3437;"
        ),
        "article_type_label": (
            "text-align:center;"
            "margin:0 0 14px 0;"
        ),
        "article_type_label_text": (
            "display:inline-block;"
            "font-size:15px;"
            "font-weight:bold;"
            "letter-spacing:0;"
            "color:#ffffff;"
            "background:#d64535;"
            "padding:6px 18px;"
            "border-radius:0;"
        ),
        "summary_outer": (
            "border:2px solid #d64535;"
            "padding:4px;"
            "margin:0 0 16px 0;"
            "background:#ffffff;"
        ),
        "summary_inner": (
            "border:1px dashed #d64535;"
            "background:#fffaf4;"
            "padding:14px 16px;"
        ),
        "summary_text": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#2f3437;"
            "margin:0 0 10px 0;"
            "text-indent:2em;"
        ),
        "body_block": (
            "background:#ffffff;"
            "border:1px solid #f0d7cc;"
            "padding:14px 16px;"
            "margin:0 0 14px 0;"
        ),
        "body_para": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#2f3437;"
            "margin:0 0 10px 0;"
            "text-indent:2em;"
        ),
        "body_bold": (
            "font-size:16px;"
            "line-height:1.8;"
            "color:#d64535;"
            "font-weight:bold;"
            "margin:0 0 10px 0;"
            "text-align:center;"
        ),
        "body_centered": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#2f3437;"
            "text-align:center;"
            "margin:0 0 8px 0;"
        ),
        "notice_info_table": (
            "border-collapse:collapse;"
            "border:none;"
            "width:100%;"
            "margin:0 0 10px 0;"
            "background:#fffaf4;"
        ),
        "notice_info_icon_cell": (
            "border:none;"
            "width:34px;"
            "padding:8px 0 8px 8px;"
            "vertical-align:top;"
        ),
        "notice_info_text_cell": (
            "border:none;"
            "padding:8px 10px;"
            "vertical-align:top;"
            "font-size:15px;"
            "line-height:1.8;"
            "color:#2f3437;"
        ),
        "notice_icon": (
            "display:block;"
            "width:22px;"
            "height:auto;"
            "border:none;"
        ),
        "notice_icon_fallback": (
            "display:inline-block;"
            "width:8px;"
            "height:8px;"
            "background:#d64535;"
            "font-size:0;"
            "line-height:0;"
            "margin-top:8px;"
        ),
        "section_title_table": (
            "border-collapse:collapse;"
            "border:none;"
            "width:100%;"
            "margin:16px 0 10px 0;"
        ),
        "section_title_cell": (
            "border:none;"
            "text-align:center;"
            "padding:8px 10px;"
            "font-size:16px;"
            "line-height:1.6;"
            "font-weight:bold;"
            "color:#d64535;"
            "background:#fff3ec;"
        ),
        "asset_divider": (
            "display:block;"
            "width:100%;"
            "height:auto;"
            "border:none;"
            "margin:14px 0;"
        ),
        "image_block": (
            "text-align:center;"
            "margin:16px 0;"
        ),
        "image": (
            "display:inline-block;"
            "max-width:100%;"
            "border:none;"
        ),
        "caption": (
            "font-size:12px;"
            "color:#8c7d75;"
            "text-align:center;"
            "margin:6px 0 8px 0;"
            "line-height:1.6;"
        ),
        "gallery_row": (
            "text-align:center;"
            "font-size:0;"
            "margin:16px 0 8px 0;"
        ),
        "gallery_item_first": (
            "display:inline-block;"
            "width:49%;"
            "vertical-align:top;"
            "font-size:14px;"
        ),
        "gallery_item_rest": (
            "display:inline-block;"
            "width:49%;"
            "vertical-align:top;"
            "font-size:14px;"
            "margin-left:1%;"
        ),
        "gallery_image": (
            "display:block;"
            "width:100%;"
            "border:none;"
        ),
        "end_block": (
            "text-align:center;"
            "padding:24px 0 16px 0;"
            "margin-top:20px;"
            "border-top:2px solid #f0d7cc;"
        ),
        "end_text": (
            "font-size:16px;"
            "font-weight:bold;"
            "color:#d64535;"
            "display:inline-block;"
            "padding:8px 20px;"
            "background:#ffffff;"
            "border:1px solid #f0d7cc;"
        ),
    }
