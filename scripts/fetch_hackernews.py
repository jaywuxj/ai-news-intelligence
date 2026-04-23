#!/usr/bin/env python3
"""
AI News Intelligence — Hacker News AI Topic Fetcher

Fetches AI/LLM related stories from Hacker News using the Algolia API.
Zero external dependencies — uses Python standard library only.

Usage:
    python3 fetch_hackernews.py
    python3 fetch_hackernews.py --query "LLM OR transformer" --limit 20
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone


def fetch_hn(query: str = "AI OR LLM OR GPT", limit: int = 15, sort: str = "date") -> list[dict]:
    """Fetch stories from Hacker News Algolia API."""
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": str(min(limit, 50)),
    }

    if sort == "date":
        base_url = "https://hn.algolia.com/api/v1/search_by_date"
    else:
        base_url = "https://hn.algolia.com/api/v1/search"

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Intelligence/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Hacker News API failed: {e}", file=sys.stderr)
        return []

    results = []
    for hit in data.get("hits", [])[:limit]:
        story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        created_at = hit.get("created_at", "")

        results.append({
            "title": hit.get("title", "Untitled"),
            "url": story_url,
            "source_name": "Hacker News",
            "source_type": "developer",
            "language": "en",
            "score": hit.get("points", 0),
            "comments_count": hit.get("num_comments", 0),
            "published_at": created_at,
            "hn_id": hit.get("objectID", ""),
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch AI stories from Hacker News")
    parser.add_argument("--query", type=str, default="AI OR LLM OR GPT OR \"large language model\"",
                        help="Search query (default: AI OR LLM OR GPT)")
    parser.add_argument("--limit", type=int, default=15, help="Max results (default: 15)")
    parser.add_argument("--sort", type=str, default="date", choices=["date", "score"],
                        help="Sort by date or score (default: date)")
    args = parser.parse_args()

    print(f"[INFO] Fetching Hacker News: query='{args.query}', limit={args.limit}", file=sys.stderr)

    results = fetch_hn(query=args.query, limit=args.limit, sort=args.sort)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"[INFO] Total: {len(results)} stories", file=sys.stderr)


if __name__ == "__main__":
    main()
