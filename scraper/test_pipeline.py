# -*- coding: utf-8 -*-
import classify, schema

raw = [
  {"id": "bahamut-1", "title": "新手前七天該做什麼", "raw_tag": "攻略", "author": "A",
   "url": "https://forum.gamer.com.tw/C.php?bsn=32564&snA=1", "source": "bahamut",
   "published_at": "2026-08-10", "views": 50, "replies": 5},
  {"id": "bahamut-2", "title": "法師轉職技能配點解析", "raw_tag": "攻略", "author": "B",
   "url": "https://forum.gamer.com.tw/C.php?bsn=32564&snA=2", "source": "bahamut",
   "published_at": "2026-08-12", "views": 900, "replies": 80},
  {"id": "bahamut-3", "title": "深淵副本II王機制拆解", "raw_tag": "攻略", "author": "C",
   "url": "https://forum.gamer.com.tw/C.php?bsn=32564&snA=3", "source": "bahamut",
   "published_at": "2026-08-01", "views": 300, "replies": 30},
  {"id": "youtube-x", "title": "改版活動全獎勵一次領", "raw_tag": "", "author": "頻道",
   "url": "https://www.youtube.com/watch?v=x", "source": "youtube",
   "published_at": "2026-08-20", "views": 12000, "replies": 300,
   "thumbnail": "https://i.ytimg.com/vi/x/hqdefault.jpg"},
  {"id": "bahamut-2", "title": "重複id應被去除", "raw_tag": "", "author": "D",
   "url": "https://forum.gamer.com.tw/C.php?bsn=32564&snA=2", "source": "bahamut",
   "published_at": "2026-08-12"},
  {"id": "", "title": "缺id應被丟棄", "raw_tag": "", "author": "E",
   "url": "https://x/", "source": "bahamut", "published_at": "2026-08-02"},
]

classify.enrich(raw)
recs = [schema.to_record(it) for it in raw]
recs = schema.dedupe(recs)
valid = [r for r in recs if not schema.validate(r)]

print("分類結果:")
for r in valid:
    print("  {:12s} -> {:6s} 精華={} tags={}".format(
        r["id"], r["category"], r["is_featured"], r["tags"]))

print()
print("去重後筆數(原6筆,重複1+缺id1應剩4):", len(valid))
print("分類涵蓋:", {r["category"] for r in valid})
print("精華(前20%約1篇,應為觀看最高的youtube-x):", [r["id"] for r in valid if r["is_featured"]])

assert len(valid) == 4, "去重/驗證筆數錯誤"
assert any(r["id"] == "youtube-x" and r["is_featured"] for r in valid), "最高互動應為精華"
assert all(r["category"] in schema.VALID_CATEGORIES for r in valid)
# 分類正確性抽驗
by_id = {r["id"]: r for r in valid}
assert by_id["bahamut-1"]["category"] == "新手指南"
assert by_id["bahamut-2"]["category"] == "職業解析"
assert by_id["bahamut-3"]["category"] == "副本攻略"
assert by_id["youtube-x"]["category"] == "活動情報"
assert "法師" in by_id["bahamut-2"]["tags"]
print()
print("=== 管線邏輯全部通過 ===")
