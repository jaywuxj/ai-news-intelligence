#!/usr/bin/env python3
"""
AI News Intelligence — RSS Feed Fetcher

Fetches AI/LLM news from curated RSS sources. Returns structured JSON to stdout.
Only includes sources with verified working RSS feeds.

Usage:
    python3 fetch_rss.py --all --since 24h --limit 10
    python3 fetch_rss.py --type official,media --since 7d
    python3 fetch_rss.py --source openai-blog,deepmind-blog
"""

import sys
import json
import re
import argparse
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip install feedparser", file=sys.stderr)
    sys.exit(1)

# ============================================================
# Built-in RSS Source Registry (only verified working feeds)
# ============================================================

SOURCES = {
    # --- 公司官方 (official) ---
    "openai-blog":      {"name": "OpenAI Blog",       "url": "https://openai.com/blog/rss.xml",                            "type": "official", "lang": "en"},
    "deepmind-blog":    {"name": "Google DeepMind",    "url": "https://deepmind.google/blog/rss.xml",                       "type": "official", "lang": "en"},
    "google-ai":        {"name": "Google AI Blog",     "url": "https://blog.google/technology/ai/rss/",                     "type": "official", "lang": "en"},
    "meta-engineering":  {"name": "Meta Engineering",   "url": "https://engineering.fb.com/feed/",                           "type": "official", "lang": "en"},
    "microsoft-ai":     {"name": "Microsoft AI",       "url": "https://blogs.microsoft.com/ai/feed/",                       "type": "official", "lang": "en"},
    "nvidia-ai":        {"name": "NVIDIA AI",          "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",  "type": "official", "lang": "en"},
    "huggingface-blog": {"name": "Hugging Face Blog",  "url": "https://huggingface.co/blog/feed.xml",                       "type": "official", "lang": "en"},

    # --- 行业媒体 (media) ---
    "theverge-ai":      {"name": "The Verge AI",       "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "media", "lang": "en"},
    "techcrunch-ai":    {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/",     "type": "media", "lang": "en"},
    "arstechnica-ai":   {"name": "Ars Technica AI",    "url": "https://arstechnica.com/ai/feed/",                                  "type": "media", "lang": "en"},
    "mit-tech-review":  {"name": "MIT Tech Review",    "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed","type": "media", "lang": "en"},
    "venturebeat-ai":   {"name": "VentureBeat AI",     "url": "https://venturebeat.com/category/ai/feed/",                         "type": "media", "lang": "en"},
    "qbitai":           {"name": "量子位",              "url": "https://www.qbitai.com/feed",                                       "type": "media", "lang": "zh"},

    # --- 学术平台 (academic) ---
    "arxiv-cs-ai":      {"name": "arXiv cs.AI",        "url": "https://rss.arxiv.org/rss/cs.AI",       "type": "academic", "lang": "en"},
    "arxiv-cs-cl":      {"name": "arXiv cs.CL",        "url": "https://rss.arxiv.org/rss/cs.CL",       "type": "academic", "lang": "en"},
    "arxiv-cs-lg":      {"name": "arXiv cs.LG",        "url": "https://rss.arxiv.org/rss/cs.LG",       "type": "academic", "lang": "en"},
}

# Sources without working RSS — must use web_search
WEBSEARCH_SOURCES = {
    # 公司官方（无 RSS）
    "anthropic":   {"name": "Anthropic",     "query": "Anthropic AI latest news OR announcement",     "type": "official"},
    "mistral":     {"name": "Mistral AI",    "query": "Mistral AI latest model release",              "type": "official"},
    "deepseek":    {"name": "DeepSeek",      "query": "DeepSeek AI latest model OR release",          "type": "official"},
    "meta-ai":     {"name": "Meta AI",       "query": "Meta AI Llama latest release",                 "type": "official"},
    "qwen":        {"name": "通义千问/Qwen",  "query": "Qwen 通义千问 latest model",                   "type": "official"},
    # 行业媒体（无 RSS）
    "jiqizhixin":  {"name": "机器之心",       "query": "机器之心 AI 最新 site:jiqizhixin.com",          "type": "media"},
    "36kr-ai":     {"name": "36氪 AI",       "query": "36氪 AI 人工智能 最新 site:36kr.com",           "type": "media"},
    "xinzhiyuan":  {"name": "新智元",         "query": "新智元 AI 最新新闻",                            "type": "media"},
    # 学术平台
    "hf-papers":   {"name": "HF Daily Papers","query": "Hugging Face daily papers trending",           "type": "academic"},
}


def parse_since(since_str: str) -> datetime:
    """Parse a relative time string like '24h', '7d' into a datetime."""
    now = datetime.now(timezone.utc)
    value = int(since_str[:-1])
    unit = since_str[-1]
    if unit == "h":
        return now - timedelta(hours=value)
    elif unit == "d":
        return now - timedelta(days=value)
    else:
        return now - timedelta(hours=24)


def parse_date(entry) -> str | None:
    """Extract and normalize publication date from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                continue
    for field in ("published", "updated"):
        val = getattr(entry, field, None)
        if val:
            return val
    return None


def fetch_one(source_id: str, source: dict, limit: int, since: datetime | None) -> list[dict]:
    """Fetch a single RSS source, return list of article dicts."""
    results = []
    try:
        feed = feedparser.parse(
            source["url"],
            agent="AI-News-Intelligence/1.0"
        )

        # Check if we got a valid feed (not HTML error page)
        if feed.bozo and not feed.entries:
            print(f"[WARN] {source['name']}: feed parse error — may need web_search fallback", file=sys.stderr)
            return []

        if not feed.entries:
            print(f"[WARN] {source['name']}: no entries found", file=sys.stderr)
            return []

        for entry in feed.entries[:limit * 2]:
            pub_date = parse_date(entry)

            # Date filter
            if since and pub_date:
                try:
                    entry_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    if entry_dt.tzinfo is None:
                        entry_dt = entry_dt.replace(tzinfo=timezone.utc)
                    if entry_dt < since:
                        continue
                except (ValueError, TypeError):
                    pass

            title = getattr(entry, "title", "Untitled") or "Untitled"
            link = getattr(entry, "link", "") or getattr(entry, "id", "")
            snippet = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
            snippet = re.sub(r"<[^>]+>", "", snippet)[:500]

            results.append({
                "title": title.strip(),
                "url": link.strip(),
                "source_id": source_id,
                "source_name": source["name"],
                "source_type": source["type"],
                "language": source["lang"],
                "published_at": pub_date,
                "content_snippet": snippet.strip(),
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[ERROR] {source['name']}: {e}", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch AI news from RSS sources")
    parser.add_argument("--type", type=str, default="", help="Source types: official,media,academic")
    parser.add_argument("--source", type=str, default="", help="Specific source IDs, comma-separated")
    parser.add_argument("--limit", type=int, default=10, help="Max articles per source (default: 10)")
    parser.add_argument("--since", type=str, default="24h", help="Time range: 1h,6h,12h,24h,48h,7d,30d")
    parser.add_argument("--all", action="store_true", help="Fetch from all RSS sources")
    parser.add_argument("--list-sources", action="store_true", help="List all available sources")
    parser.add_argument("--list-websearch", action="store_true", help="List sources that need web_search")
    args = parser.parse_args()

    if args.list_sources:
        print("=== RSS Sources (working, built-in) ===")
        for sid, s in sorted(SOURCES.items()):
            print(f"  {sid:20s}  [{s['type']:10s}]  {s['name']}")
        return

    if args.list_websearch:
        print("=== Web Search Sources (no RSS, use web_search with these queries) ===")
        for sid, s in sorted(WEBSEARCH_SOURCES.items()):
            print(f"  {sid:15s}  [{s['type']:10s}]  {s['name']}")
            print(f"  {'':15s}  query: {s['query']}")
        return

    selected = {}
    if args.all:
        selected = dict(SOURCES)
    elif args.source:
        for sid in args.source.split(","):
            sid = sid.strip()
            if sid in SOURCES:
                selected[sid] = SOURCES[sid]
            elif sid in WEBSEARCH_SOURCES:
                ws = WEBSEARCH_SOURCES[sid]
                print(f"[INFO] {ws['name']}: no RSS available. Use web_search with query: {ws['query']}", file=sys.stderr)
            else:
                print(f"[WARN] Unknown source ID: {sid}. Use --list-sources to see available IDs.", file=sys.stderr)
    elif args.type:
        types = set(t.strip() for t in args.type.split(","))
        for sid, s in SOURCES.items():
            if s["type"] in types:
                selected[sid] = s
        # Also hint about web_search sources for the same types
        ws_hints = [s for s in WEBSEARCH_SOURCES.values() if s["type"] in types]
        if ws_hints:
            print(f"[INFO] {len(ws_hints)} additional sources for these types need web_search:", file=sys.stderr)
            for s in ws_hints:
                print(f"  - {s['name']}: web_search \"{s['query']}\"", file=sys.stderr)
    else:
        for sid, s in SOURCES.items():
            if s["type"] in ("official", "media"):
                selected[sid] = s

    if not selected:
        print("No sources selected. Use --all, --type, or --source. Try --list-sources.", file=sys.stderr)
        sys.exit(1)

    since_dt = parse_since(args.since)
    print(f"[INFO] Fetching {len(selected)} RSS sources, since {args.since}, limit {args.limit}/source", file=sys.stderr)

    all_articles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_one, sid, src, args.limit, since_dt): sid
            for sid, src in selected.items()
        }
        for future in as_completed(futures):
            articles = future.result()
            all_articles.extend(articles)

    all_articles.sort(key=lambda a: a.get("published_at") or "0", reverse=True)

    print(json.dumps(all_articles, ensure_ascii=False, indent=2))
    print(f"[INFO] Total: {len(all_articles)} articles from {len(selected)} RSS sources", file=sys.stderr)


if __name__ == "__main__":
    main()
