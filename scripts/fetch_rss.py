#!/usr/bin/env python3
"""
AI News Intelligence — RSS Feed Fetcher

Fetches AI/LLM news from curated RSS sources. Returns structured JSON to stdout.

Usage:
    python3 fetch_rss.py --all --since 24h --limit 10
    python3 fetch_rss.py --type official,media --since 7d
    python3 fetch_rss.py --source openai-blog,anthropic-news
"""

import sys
import json
import argparse
import hashlib
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip install feedparser", file=sys.stderr)
    sys.exit(1)

# ============================================================
# Built-in RSS Source Registry
# ============================================================

SOURCES = {
    # --- 公司官方 (official) ---
    "openai-blog":      {"name": "OpenAI Blog",       "url": "https://openai.com/blog/rss.xml",                            "type": "official", "lang": "en"},
    "anthropic-news":   {"name": "Anthropic News",     "url": "https://www.anthropic.com/rss.xml",                          "type": "official", "lang": "en"},
    "deepmind-blog":    {"name": "Google DeepMind",    "url": "https://deepmind.google/blog/rss.xml",                       "type": "official", "lang": "en"},
    "google-ai":        {"name": "Google AI Blog",     "url": "https://blog.google/technology/ai/rss/",                     "type": "official", "lang": "en"},
    "meta-ai":          {"name": "Meta AI",            "url": "https://ai.meta.com/blog/rss/",                              "type": "official", "lang": "en"},
    "microsoft-ai":     {"name": "Microsoft AI",       "url": "https://blogs.microsoft.com/ai/feed/",                       "type": "official", "lang": "en"},
    "nvidia-ai":        {"name": "NVIDIA AI",          "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",  "type": "official", "lang": "en"},
    "huggingface-blog": {"name": "Hugging Face Blog",  "url": "https://huggingface.co/blog/feed.xml",                       "type": "official", "lang": "en"},
    "mistral-news":     {"name": "Mistral AI",         "url": "https://mistral.ai/feed.xml",                                "type": "official", "lang": "en"},

    # --- 行业媒体 (media) ---
    "theverge-ai":      {"name": "The Verge AI",       "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "media", "lang": "en"},
    "techcrunch-ai":    {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/",     "type": "media", "lang": "en"},
    "arstechnica-ai":   {"name": "Ars Technica AI",    "url": "https://arstechnica.com/ai/feed/",                                  "type": "media", "lang": "en"},
    "mit-tech-review":  {"name": "MIT Tech Review",    "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed","type": "media", "lang": "en"},
    "venturebeat-ai":   {"name": "VentureBeat AI",     "url": "https://venturebeat.com/category/ai/feed/",                         "type": "media", "lang": "en"},
    "jiqizhixin":       {"name": "机器之心",            "url": "https://www.jiqizhixin.com/rss",                                    "type": "media", "lang": "zh"},
    "qbitai":           {"name": "量子位",              "url": "https://www.qbitai.com/feed",                                       "type": "media", "lang": "zh"},
    "36kr-ai":          {"name": "36氪 AI",            "url": "https://36kr.com/feed",                                              "type": "media", "lang": "zh"},

    # --- 学术平台 (academic) ---
    "arxiv-cs-ai":      {"name": "arXiv cs.AI",        "url": "https://rss.arxiv.org/rss/cs.AI",       "type": "academic", "lang": "en"},
    "arxiv-cs-cl":      {"name": "arXiv cs.CL",        "url": "https://rss.arxiv.org/rss/cs.CL",       "type": "academic", "lang": "en"},
    "hf-papers":        {"name": "HF Daily Papers",    "url": "https://huggingface.co/papers/rss",      "type": "academic", "lang": "en"},

    # --- 开发者社区 (developer) ---
    "hn-ai":            {"name": "Hacker News AI",     "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT&count=20", "type": "developer", "lang": "en"},
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
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            print(f"[WARN] {source['name']}: feed parse error", file=sys.stderr)
            return []

        for entry in feed.entries[:limit * 2]:  # fetch extra to allow date filtering
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
            # Clean HTML tags from snippet
            import re
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
    parser.add_argument("--type", type=str, default="", help="Source types: official,media,academic,developer")
    parser.add_argument("--source", type=str, default="", help="Specific source IDs, comma-separated")
    parser.add_argument("--limit", type=int, default=10, help="Max articles per source (default: 10)")
    parser.add_argument("--since", type=str, default="24h", help="Time range: 1h,6h,12h,24h,48h,7d,30d")
    parser.add_argument("--all", action="store_true", help="Fetch from all sources")
    parser.add_argument("--list-sources", action="store_true", help="List all available source IDs")
    args = parser.parse_args()

    # List mode
    if args.list_sources:
        for sid, s in sorted(SOURCES.items()):
            print(f"  {sid:20s}  [{s['type']:10s}]  {s['name']}")
        return

    # Determine which sources to fetch
    selected = {}
    if args.all:
        selected = dict(SOURCES)
    elif args.source:
        for sid in args.source.split(","):
            sid = sid.strip()
            if sid in SOURCES:
                selected[sid] = SOURCES[sid]
            else:
                print(f"[WARN] Unknown source ID: {sid}", file=sys.stderr)
    elif args.type:
        types = set(t.strip() for t in args.type.split(","))
        for sid, s in SOURCES.items():
            if s["type"] in types:
                selected[sid] = s
    else:
        # Default: official + media
        for sid, s in SOURCES.items():
            if s["type"] in ("official", "media"):
                selected[sid] = s

    if not selected:
        print("No sources selected. Use --all, --type, or --source.", file=sys.stderr)
        sys.exit(1)

    since_dt = parse_since(args.since)
    print(f"[INFO] Fetching {len(selected)} sources, since {args.since}, limit {args.limit}/source", file=sys.stderr)

    # Parallel fetch
    all_articles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_one, sid, src, args.limit, since_dt): sid
            for sid, src in selected.items()
        }
        for future in as_completed(futures):
            articles = future.result()
            all_articles.extend(articles)

    # Sort by date (newest first), handle None dates
    all_articles.sort(key=lambda a: a.get("published_at") or "0", reverse=True)

    # Output
    print(json.dumps(all_articles, ensure_ascii=False, indent=2))
    print(f"[INFO] Total: {len(all_articles)} articles from {len(selected)} sources", file=sys.stderr)


if __name__ == "__main__":
    main()
