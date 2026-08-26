#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取全球 AI 新闻，输出结构化 JSON 供 agent 做中文摘要与筛选。

用法:
  python news_digest.py fetch --limit 12

输出 JSON:
{
  "date": "2026-08-21",
  "items": [
    {"title": "...", "link": "...", "source": "TechCrunch", "published": "...", "summary": "..."}
  ]
}
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import Request, urlopen

SOURCES = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "type": "rss",
    },
    {
        "name": "MIT Tech Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "type": "rss",
    },
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_rss(src, limit):
    """抓取并解析 RSS，返回条目列表。"""
    req = Request(src["url"], headers=UA)
    with urlopen(req, timeout=20) as r:
        data = r.read().decode("utf-8", errors="replace")
    root = ET.fromstring(data)
    items = []
    for item in root.iter("item"):
        title = _text(item, "title")
        link = _text(item, "link")
        pub = _text(item, "pubDate")
        desc = _text(item, "description")
        summary = _strip_html(desc)[:400]
        items.append({
            "title": title,
            "link": link,
            "source": src["name"],
            "published": pub,
            "summary": summary,
        })
        if len(items) >= limit:
            break
    return items


def _text(el, tag):
    for child in el.iter(tag):
        if child.text:
            return child.text.strip()
    return ""


def _strip_html(html):
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch(limit):
    all_items = []
    for src in SOURCES:
        try:
            all_items.extend(fetch_rss(src, limit))
        except Exception as e:
            all_items.append({
                "title": f"[{src['name']} 抓取失败]",
                "link": src["url"],
                "source": src["name"],
                "published": "",
                "summary": str(e)[:200],
            })
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": all_items,
    }


if __name__ == "__main__":
    limit = 12
    if len(sys.argv) >= 4 and sys.argv[2] == "--limit":
        limit = int(sys.argv[3])
    result = fetch(limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
