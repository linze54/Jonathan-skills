#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify a source document into the supported WeChat article types."""

import re


NOTICE_TERMS = (
    "通知", "公告", "预告", "招募", "报名", "邀您", "邀请", "参与方式", "报名方式",
    "活动时间", "活动地点", "活动对象", "参与对象", "服务对象", "活动安排", "活动流程",
    "截止", "截至", "扫码", "联系电话", "联系人", "请于", "将于", "拟于",
)

BRIEFING_TERMS = (
    "简报", "回顾", "总结", "圆满结束", "圆满举行", "圆满举办", "成功举办", "成功举行",
    "顺利开展", "顺利举行", "顺利举办", "活动现场", "本次活动", "此次活动",
    "参与居民", "参与人数", "活动中", "活动后", "取得", "成效", "成果", "合影",
)

NOTICE_FIELD_TERMS = ("时间", "地点", "对象", "报名", "截止", "联系人", "联系电话", "活动安排")
DATE_RE = re.compile(r"\d{1,2}[月/-]\d{1,2}[日号]?|\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日号]?")
TIME_RE = re.compile(r"\d{1,2}[:：]\d{2}|\d{1,2}点|\d{1,2}:\d{2}")


def _iter_texts(blocks: list):
    for block in blocks:
        if block.get("text"):
            yield str(block.get("text"))
        for para in block.get("paragraphs", []) or []:
            if para.get("text"):
                yield str(para.get("text"))
        for image in block.get("images", []) or []:
            if image.get("caption"):
                yield str(image.get("caption"))
        if block.get("caption"):
            yield str(block.get("caption"))
        if block.get("shared_caption"):
            yield str(block.get("shared_caption"))


def classify_article_type(blocks: list, doc_info: dict | None = None, images_count: int = 0) -> dict:
    """Return a small classification payload for downstream rendering.

    Supported values:
    - activity_notice
    - activity_briefing
    """
    doc_info = doc_info or {}
    texts = [t.strip() for t in _iter_texts(blocks) if t and t.strip()]
    full_text = "\n".join(texts)
    compact_doc_type = str(doc_info.get("doc_type", "")).replace(" ", "")

    notice_score = 0
    briefing_score = 0
    notice_signals = []
    briefing_signals = []

    for term in NOTICE_TERMS:
        if term in full_text or term in compact_doc_type:
            notice_score += 2 if term in ("通知", "公告", "报名", "招募") else 1
            notice_signals.append(term)

    for term in BRIEFING_TERMS:
        if term in full_text or term in compact_doc_type:
            briefing_score += 2 if term in ("简报", "回顾", "圆满结束", "成功举办") else 1
            briefing_signals.append(term)

    field_hits = sum(1 for term in NOTICE_FIELD_TERMS if term in full_text)
    if field_hits >= 3:
        notice_score += field_hits
        notice_signals.append("notice_fields")

    if DATE_RE.search(full_text) and TIME_RE.search(full_text):
        notice_score += 2
        notice_signals.append("date_time")

    # Notice documents often have no event photos. Briefings usually do.
    if images_count == 0 and notice_score > 0:
        notice_score += 2
        notice_signals.append("no_images")
    elif images_count >= 2:
        briefing_score += 1
        briefing_signals.append("images_present")

    if "通知" in compact_doc_type or "公告" in compact_doc_type:
        notice_score += 4
    if "简报" in compact_doc_type or "总结" in compact_doc_type:
        briefing_score += 4

    article_type = "activity_notice" if notice_score > briefing_score else "activity_briefing"
    confidence = abs(notice_score - briefing_score)
    return {
        "article_type": article_type,
        "notice_score": notice_score,
        "briefing_score": briefing_score,
        "confidence": confidence,
        "signals": {
            "activity_notice": sorted(set(notice_signals)),
            "activity_briefing": sorted(set(briefing_signals)),
        },
    }
