#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
caption_matcher.py — 将 caption_candidate 元素绑定到相邻图片

绑定规则（按优先级）：
1. image 后紧跟 caption_candidate（最常见）
2. caption_candidate 后紧跟 image
3. empty 段落不阻断绑定（允许中间有一个 empty）
4. 已绑定的 caption_candidate 从序列中移除，避免重复使用
"""


def _is_adjacent(elements, i, j, max_gap=2) -> bool:
    """判断 i 和 j 之间是否只有 empty 元素（允许最多 max_gap 个）。"""
    lo, hi = min(i, j), max(i, j)
    gap_count = 0
    for k in range(lo + 1, hi):
        if elements[k]["kind"] != "empty":
            return False
        gap_count += 1
        if gap_count > max_gap:
            return False
    return True


def match_captions(elements: list) -> list:
    """
    遍历 elements，将 caption_candidate 绑定到相邻图片。
    返回新的 elements 列表，caption_candidate 已被消费（kind 改为 "consumed"）。
    图片元素增加 "caption" 字段（str 或 None）。
    """
    n = len(elements)
    # 初始化所有图片的 caption 为 None
    for elem in elements:
        if elem["kind"] == "image":
            elem.setdefault("caption", None)

    consumed = set()

    for i, elem in enumerate(elements):
        if elem["kind"] != "image":
            continue
        if elem.get("caption") is not None:
            continue

        # 向后找最近的 caption_candidate
        for j in range(i + 1, min(i + 4, n)):
            if j in consumed:
                continue
            if elements[j]["kind"] == "caption_candidate" and _is_adjacent(elements, i, j):
                elem["caption"] = elements[j]["text"]
                consumed.add(j)
                break
            if elements[j]["kind"] not in ("empty",):
                break

        # 向前找（fallback）
        if elem.get("caption") is None:
            for j in range(i - 1, max(i - 4, -1), -1):
                if j in consumed:
                    continue
                if elements[j]["kind"] == "caption_candidate" and _is_adjacent(elements, j, i):
                    elem["caption"] = elements[j]["text"]
                    consumed.add(j)
                    break
                if elements[j]["kind"] not in ("empty",):
                    break

    # 标记已消费的 caption_candidate
    result = []
    for i, elem in enumerate(elements):
        if i in consumed:
            elem = dict(elem)
            elem["kind"] = "consumed"
        result.append(elem)

    return result
