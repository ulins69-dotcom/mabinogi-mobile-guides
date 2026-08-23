# -*- coding: utf-8 -*-
"""
資料管線代理人 —— 總指揮。
流程：爬取(巴哈+YouTube) → 分類/打標/評精華 → 去重 → schema 驗證 → 產出 guides.json

用法：
    python main.py                # 完整跑（需 YOUTUBE_API_KEY）
    python main.py --no-youtube   # 只跑巴哈（無金鑰時）
    python main.py --out ../guides.json
"""

from __future__ import annotations
import argparse
import datetime
import json
import sys

import bahamut
import youtube
import classify
import schema


def build(no_youtube: bool = False, pages: int = 2) -> dict:
    raw = []

    # 1) 爬取
    raw.extend(bahamut.fetch(pages=pages))
    if not no_youtube:
        try:
            raw.extend(youtube.fetch())
        except Exception as e:
            print(f"[主控] YouTube 略過（{e}）", file=sys.stderr)

    if not raw:
        print("[主控] 警告：未取得任何資料，將產生空清單")

    # 2) 分類 / 打標 / 評精華（可抽換模組）
    classify.enrich(raw)

    # 3) 轉合約格式 → 去重 → 驗證
    records = [schema.to_record(it) for it in raw]
    records = schema.dedupe(records)

    valid, dropped = [], 0
    for r in records:
        problems = schema.validate(r)
        if problems:
            dropped += 1
            print(f"[主控] 丟棄不合格資料 {r.get('id')}: {problems}")
        else:
            valid.append(r)

    # 4) 依日期新→舊排序
    valid.sort(key=lambda r: r.get("published_at", ""), reverse=True)

    print(f"[主控] 有效 {len(valid)} 筆，丟棄 {dropped} 筆，精華 {sum(1 for r in valid if r['is_featured'])} 筆")
    return {
        "updated_at": datetime.date.today().isoformat(),
        "guides": valid,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-youtube", action="store_true", help="不呼叫 YouTube API")
    ap.add_argument("--pages", type=int, default=2, help="巴哈列表抓幾頁")
    ap.add_argument("--out", default="guides.json", help="輸出路徑")
    args = ap.parse_args()

    result = build(no_youtube=args.no_youtube, pages=args.pages)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[主控] 已寫出 {args.out}")


if __name__ == "__main__":
    main()
