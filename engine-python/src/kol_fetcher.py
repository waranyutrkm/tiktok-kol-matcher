"""
Step 2 of the pipeline: build a candidate pool of Thai TikTok creators.

Because TikTok's official Research API is gated to academics with brutal rate
limits, we use Apify's public-data TikTok scraper as the production data source.
In DEMO_MODE we load a bundled sample so the whole pipeline runs with no keys.
"""
from __future__ import annotations
import json
import os
from typing import List, Dict

from . import config

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_demo() -> List[Dict]:
    with open(os.path.join(_DATA_DIR, "demo_kols.json"), encoding="utf-8") as f:
        return json.load(f)


def _normalize_apify_item(item: Dict) -> Dict:
    """Map raw Apify TikTok output into our internal schema.
    Field names vary by actor; adjust here if you swap actors."""
    author = item.get("authorMeta", item)
    stats = item.get("authorStats", author)
    return {
        "username": author.get("name") or author.get("uniqueId", ""),
        "url": f"https://www.tiktok.com/@{author.get('name') or author.get('uniqueId','')}",
        "nickname": author.get("nickName") or author.get("nickname", ""),
        "bio": author.get("signature", ""),
        "region": author.get("region", ""),
        "language": author.get("language", ""),
        "categories": [],  # inferred later from bio/hashtags
        "followers": stats.get("fans") or stats.get("followerCount", 0),
        "avg_views": author.get("avgViews", 0),
        "avg_likes": stats.get("heart") or stats.get("heartCount", 0),
        "avg_comments": 0,
        "avg_shares": 0,
        "video_count": stats.get("video") or stats.get("videoCount", 0),
        "verified": author.get("verified", False),
        "recent_hashtags": [h.get("name") for h in item.get("hashtags", []) if h.get("name")],
    }


def fetch_kols_apify(search_terms: List[str], per_term: int = 20,
                     region: str = "TH") -> List[Dict]:
    """Query Apify TikTok scraper by search terms / hashtags."""
    from apify_client import ApifyClient
    client = ApifyClient(config.APIFY_TOKEN)
    run_input = {
        "searchQueries": search_terms,
        "resultsPerPage": per_term,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "proxyConfiguration": {"useApifyProxy": True},
    }
    run = client.actor(config.APIFY_TIKTOK_ACTOR).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    seen, out = set(), []
    for it in items:
        norm = _normalize_apify_item(it)
        if norm["username"] and norm["username"] not in seen:
            seen.add(norm["username"])
            out.append(norm)
    return out


def get_candidate_kols(search_terms: List[str], region: str = "TH") -> List[Dict]:
    """Main entry point. Returns list of candidate creator dicts."""
    if config.DEMO_MODE or not config.APIFY_TOKEN:
        return _load_demo()
    try:
        kols = fetch_kols_apify(search_terms, region=region)
        return kols or _load_demo()
    except Exception as e:
        print(f"[kol_fetcher] Apify fetch failed, falling back to demo pool: {e}")
        return _load_demo()
