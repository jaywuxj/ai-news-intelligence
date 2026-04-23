#!/usr/bin/env python3
"""
AI News Intelligence — Hacker News AI Topic Fetcher

Fetches AI/LLM related stories from Hacker News using two strategies:
1. Front Page mode (default): gets current HN front page, filters for AI topics
2. Search mode: uses Algolia search API for keyword search

Zero external dependencies — uses Python standard library only.

Usage:
    python3 fetch_hackernews.py                           # Front page AI stories
    python3 fetch_hackernews.py --mode search --query "LLM"  # Search mode
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone

AI_KEYWORDS = [
    "ai", "llm", "gpt", "openai", "anthropic", "claude", "gemini", "deepseek",
    "mistral", "llama", "transformer", "neural", "machine learn", "deep learn",
    "large language", "chatgpt", "copilot", "diffusion", "multimodal",
    "agent", "rag", "fine-tun", "embedding", "hugging face", "pytorch",
    "tensorflow", "model", "inference", "training", "gpu", "nvidia", "cuda",
    "alignment", "rlhf", "reasoning", "benchmark", "token", "prompt",
    "大模型", "人工智能",
]


def is_ai_related(title: str) -> bool:
    """Check if a title is AI related based on keyword matching."""
    t = title.lower()
    return any(kw in t for kw in AI_KEYWORDS)


def fetch_front_page(limit: int = 15) -> list[dict]:
    """Fetch HN front page and filter for AI-related stories."""
    results = []

    try:
        # Get front page story IDs from Algolia (more reliable than Firebase for bulk)
        url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=50"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Intelligence/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if not is_ai_related(title):
                continue

            story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            hn_url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

            results.append({
                "title": title,
                "url": story_url,
                "hn_url": hn_url,
                "source_name": "Hacker News",
                "source_type": "developer",
                "language": "en",
                "score": hit.get("points", 0),
                "comments_count": hit.get("num_comments", 0),
                "published_at": hit.get("created_at", ""),
                "hn_id": hit.get("objectID", ""),
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[ERROR] HN front page fetch failed: {e}", file=sys.stderr)

    # If front page has no AI content, fall back to recent search
    if not results:
        print("[INFO] No AI stories on front page, falling back to recent search", file=sys.stderr)
        results = fetch_search("AI OR LLM OR GPT", limit=limit, sort="date")

    return results


def fetch_search(query: str = "AI OR LLM OR GPT", limit: int = 15, sort: str = "date") -> list[dict]:
    """Search HN via Algolia API."""
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": str(min(limit * 3, 50)),  # fetch extra to filter quality
        "numericFilters": "points>5",  # filter low quality
    }

    if sort == "date":
        base_url = "https://hn.algolia.com/api/v1/search_by_date"
    else:
        base_url = "https://hn.algolia.com/api/v1/search"

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Intelligence/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        for hit in data.get("hits", [])[:limit]:
            story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            hn_url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

            results.append({
                "title": hit.get("title", "Untitled"),
                "url": story_url,
                "hn_url": hn_url,
                "source_name": "Hacker News",
                "source_type": "developer",
                "language": "en",
                "score": hit.get("points", 0),
                "comments_count": hit.get("num_comments", 0),
                "published_at": hit.get("created_at", ""),
                "hn_id": hit.get("objectID", ""),
            })

    except Exception as e:
        print(f"[ERROR] HN search failed: {e}", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch AI stories from Hacker News")
    parser.add_argument("--mode", type=str, default="front_page", choices=["front_page", "search"],
                        help="front_page (default): filter AI from HN front page; search: keyword search")
    parser.add_argument("--query", type=str, default="AI OR LLM OR GPT OR \"large language model\"",
                        help="Search query (only used in search mode)")
    parser.add_argument("--limit", type=int, default=15, help="Max results (default: 15)")
    parser.add_argument("--sort", type=str, default="date", choices=["date", "score"],
                        help="Sort by date or score (search mode only)")
    args = parser.parse_args()

    if args.mode == "front_page":
        print(f"[INFO] Fetching HN front page, filtering AI topics, limit={args.limit}", file=sys.stderr)
        results = fetch_front_page(limit=args.limit)
    else:
        print(f"[INFO] Searching HN: query='{args.query}', limit={args.limit}, sort={args.sort}", file=sys.stderr)
        results = fetch_search(query=args.query, limit=args.limit, sort=args.sort)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"[INFO] Total: {len(results)} stories", file=sys.stderr)


if __name__ == "__main__":
    main()
