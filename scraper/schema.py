# -*- coding: utf-8 -*-
"""
資料合約（Schema）守門員。
產出 guides.json 前，每一筆都必須通過 to_record() 正規化，
確保欄位齊全、型別正確——與前端 index.html 的 normalize() 兩邊對齊。
"""

from __future__ import annotations

VALID_CATEGORIES = {"新手指南", "職業解析", "副本攻略", "活動情報"}
VALID_SOURCES = {"bahamut", "youtube", "official"}


def _s(v, fallback="") -> str:
    return v if isinstance(v, str) and v else fallback


def to_record(item: dict) -> dict:
    """把內部工作用 dict 轉成符合合約的乾淨紀錄。"""
    category = _s(item.get("category"), "新手指南")
    if category not in VALID_CATEGORIES:
        category = "新手指南"

    source = _s(item.get("source"), "bahamut")
    if source not in VALID_SOURCES:
        source = "bahamut"

    tags = item.get("tags") or []
    tags = [t for t in tags if isinstance(t, str) and t]

    return {
        "id": _s(item.get("id")),
        "title": _s(item.get("title"), "（無標題）"),
        "author": _s(item.get("author"), "未知"),
        "category": category,
        "tags": tags,
        "url": _s(item.get("url")),
        "summary": _s(item.get("summary")),
        "source": source,
        "published_at": _s(item.get("published_at")),
        "is_featured": item.get("is_featured") is True,
        "thumbnail": _s(item.get("thumbnail")),
    }


def validate(record: dict) -> list[str]:
    """回傳問題清單，空清單代表通過。"""
    problems = []
    if not record.get("id"):
        problems.append("缺少 id")
    if not record.get("url"):
        problems.append("缺少 url")
    if record.get("category") not in VALID_CATEGORIES:
        problems.append(f"category 非法：{record.get('category')}")
    if record.get("source") not in VALID_SOURCES:
        problems.append(f"source 非法：{record.get('source')}")
    if not isinstance(record.get("tags"), list):
        problems.append("tags 非陣列")
    return problems


def dedupe(records: list[dict]) -> list[dict]:
    """以 id 去重，保留第一筆。"""
    seen = set()
    out = []
    for r in records:
        rid = r.get("id")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        out.append(r)
    return out
