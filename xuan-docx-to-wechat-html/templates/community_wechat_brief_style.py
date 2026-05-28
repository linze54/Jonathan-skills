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

        # 标题区（文档标题）
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
        
        # 推文标题区（新增）
        "article_title_wrap": (
            "text-align:center;"
            "padding:24px 8px 8px 8px;"
            "border-bottom:1px solid #e8ddd0;"  # 添加底部边框，与正文区分
            "margin-bottom:16px;"
        ),
        "article_title": (
            "font-size:22px;"  # 比文档标题稍大
            "font-weight:bold;"
            "color:#c0392b;"  # 使用红色，更醒目
            "line-height:1.6;"
            "margin:0 0 12px 0;"  # 增加下边距
        ),
        "article_subtitle": (
            "font-size:18px;"
            "font-weight:normal;"
            "color:#2c2420;"
            "line-height:1.5;"
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

        # 活动总述卡片（summary）- 微信兼容版：双层边框效果
        # 外层：红色实线边框
        "summary_outer": (
            "border:2px solid #c0392b;"
            "padding:4px;"
            "margin-bottom:16px;"
        ),
        # 内层：浅色虚线边框 + 白底内容区
        "summary_inner": (
            "border:1px dashed #c0392b;"
            "background:#ffffff;"
            "padding:14px 16px;"
        ),
        "summary_text": (
            "font-size:15px;"
            "line-height:1.9;"
            "color:#3d3530;"
            "margin:0 0 10px 0;"
            "text-indent:2em;"
        ),

        # 正文块 - 微信兼容版：白底凸显文字内容
        "body_block": (
            "background:#ffffff;"  # 白底凸显文字内容
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

        # 单图块 - 微信兼容版：图片居中
        "image_block": (
            "text-align:center;"  # 图片居中
            "margin:16px 0;"
        ),
        "image": (
            "display:inline-block;"  # 配合父容器的text-align:center
            "max-width:100%;"  # 限制最大宽度
        ),

        # 图注
        "caption": (
            "font-size:12px;"
            "color:#9e8e82;"
            "text-align:center;"
            "margin:6px 0 8px 0;"
            "line-height:1.6;"
        ),

        # 双图并排：微信兼容版，上下图片之间有空隙
        # 每行最多2张，使用inline-block布局
        "gallery_row": (
            "text-align:center;"  # 图片居中
            "font-size:0;"  # 消除inline-block间隙
            "margin:16px 0 8px 0;"  # 上下图片之间有空隙
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

        # 文末收束区 - 微信兼容版：父容器text-align:center实现居中
        "end_block": (
            "text-align:center;"  # 父容器居中，最稳的微信兼容方式
            "padding:24px 0 16px 0;"
            "margin-top:24px;"
            "border-top:2px solid #e8ddd0;"
        ),
        "end_text": (
            "font-size:16px;"
            "font-weight:bold;"
            "color:#c0392b;"
            "display:inline-block;"  # 配合父容器的text-align:center
            "padding:8px 20px;"
            "background:#ffffff;"  # 白底
            "border:1px solid #e8ddd0;"
        ),
    }
