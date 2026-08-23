# -*- coding: utf-8 -*-
"""
YouTube Data API v3 攻略影片抓取。

【Phase 0 配額鐵則】
- 每日免費 10,000 units。
- search.list = 100 units/次（貴）→ 每個關鍵字只搜一次。
- videos.list = 1 unit/次（便宜）→ 批次抓詳情（一次最多 50 支）。
策略：少數關鍵字 search.list 拿 videoId → 合併去重 → 一次 videos.list 抓詳情。
每週跑一次遠低於配額。

金鑰請放環境變數 YOUTUBE_API_KEY（GitHub Actions 用 Secrets），切勿寫死在程式裡。
"""

from __future__ import annotations
import os
import requests

API_BASE = "https://www.googleapis.com/youtube/v3"

# 搜尋用關鍵字（每個關鍵字花 100 units，控制數量）
SEARCH_QUERIES = [
    "瑪奇 Mobile 攻略",
    "瑪奇 Mobile 新手",
    "瑪奇 Mobile 活動",
]
MAX_PER_QUERY = 15  # 每個關鍵字取幾支


def _key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("環境變數 YOUTUBE_API_KEY 未設定")
    return key


def _search_ids(query: str, key: str) -> list[str]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": MAX_PER_QUERY,
        "relevanceLanguage": "zh-Hant",
        "order": "relevance",
        "key": key,
    }
    r = requests.get(f"{API_BASE}/search", params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]


def _video_details(video_ids: list[str], key: str) -> list[dict]:
    out = []
    # videos.list 一次最多 50 支
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        params = {
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "key": key,
        }
        r = requests.get(f"{API_BASE}/videos", params=params, timeout=15)
        r.raise_for_status()
        for it in r.json().get("items", []):
            sn = it.get("snippet", {})
            st = it.get("statistics", {})
            vid = it.get("id", "")
            thumbs = sn.get("thumbnails", {})
            thumb = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url", "")
            out.append({
                "id": f"youtube-{vid}",
                "title": sn.get("title", ""),
                "raw_tag": "",
                "author": sn.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "summary": (sn.get("description", "") or "")[:120],
                "source": "youtube",
                "published_at": (sn.get("publishedAt", "") or "")[:10],
                "views": int(st.get("viewCount", 0) or 0),
                "replies": int(st.get("commentCount", 0) or 0),
                "thumbnail": thumb,
            })
    return out


def fetch() -> list[dict]:
    key = _key()
    ids = []
    for q in SEARCH_QUERIES:
        print(f"[YT] 搜尋：{q}")
        try:
            ids.extend(_search_ids(q, key))
        except requests.RequestException as e:
            print(f"[YT] 搜尋失敗 {q}: {e}")
    ids = list(dict.fromkeys(ids))  # 去重保序
    print(f"[YT] 去重後 {len(ids)} 支影片，批次抓詳情")
    items = _video_details(ids, key) if ids else []
    print(f"[YT] 共取得 {len(items)} 筆")
    return items
