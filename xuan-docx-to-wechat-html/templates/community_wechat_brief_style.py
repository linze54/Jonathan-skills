#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
community_wechat_brief_style.py — 社区活动简报风格
v2: 微信公众号兼容版，移除 flex/grid，嵌套≤3层，图片 display:block;width:100%
"""


def get_styles() -> dict:
    return {
        # 外层容器（微信控制宽度，不设 max-width）
        "wrap": (
            "margin:0 auto;"
            "padding:16px 12px;"
            "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
            "background:#faf8f5;"
            "color:#3d3530;"
        ),

        # 标题区
        "title_wrap": (
            "text-align:center;"
            "padding:24px 8px 8px 8px;"
        ),
        "title": (
            "font-size:20px;"
            "font-weight:bold;"
            "color:#2c2420;"
            "line-height:1.6;"
            "margin:0 0 8px 0;"
        ),

        # 元信息区
        "meta_wrap": (
            "text-align:center;"
            "padding:4px 8px 20px 8px;"
            "border-bottom:1px solid #e8ddd0;"
            "margin-bottom:16px;"
        ),
        "meta_line": (
            "font-size:13px;"
            "color:#9e8e82;"
            "line-height:2;"
        ),

        # 活动总述卡片（summary）
        "summary_block": (
            "background:#fdf6ee;"
            "border-left:3px solid #c0392b;"
            "padding:14px 16px;"
            "margin-bottom:16px;"
        ),
        "summary_text": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "margin:0 0 10px 0;"
            "text-indent:2em;"
        ),

        # 正文块
        "body_block": (
            "background:#fdf6ee;"
            "border:1px solid #e8ddd0;"
            "padding:14px 16px;"
            "margin-bottom:14px;"
        ),
        "body_para": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "margin:0 0 10px 0;"
            "text-indent:2em;"
        ),
        "body_bold": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#2c2420;"
            "font-weight:bold;"
            "margin:0 0 8px 0;"
        ),
        "body_centered": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "text-align:center;"
            "margin:0 0 8px 0;"
        ),

        # 单图块（display:block;width:100% 符合微信规范）
        "image_block": (
            "margin:16px 0;"
        ),
        "image": (
            "display:block;"
            "width:100%;"
        ),

        # 图注
        "caption": (
            "font-size:12px;"
            "color:#9e8e82;"
            "text-align:center;"
            "margin:6px 0 8px 0;"
            "line-height:1.6;"
        ),

        # 双图并排：inline-block + font-size:0 消除间距（无 flex/grid）
        # 每行最多2张，超出自动换行
        "gallery_row": (
            "text-align:center;"
            "font-size:0;"
            "margin:16px 0 4px 0;"
        ),
        # 第一张图（无左边距）
        "gallery_item_first": (
            "display:inline-block;"
            "width:49%;"
            "vertical-align:top;"
            "font-size:14px;"
        ),
        # 第二张图（有左边距）
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
        ),

        # 文末收束区
        "end_block": (
            "text-align:center;"
            "padding:20px 0 12px 0;"
            "margin-top:20px;"
            "border-top:1px solid #e8ddd0;"
        ),
        "end_text": (
            "font-size:13px;"
            "color:#c0392b;"
        ),
    }
