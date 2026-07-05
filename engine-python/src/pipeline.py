"""End-to-end orchestration: brand input to ranked TikTok creator shortlist."""
from __future__ import annotations

from typing import Dict, List

from . import config
from .brand_analyzer import BrandProfile, analyze_brand
from .kol_fetcher import get_candidate_kols
from .matcher import add_rationales, score_kols
from .planner import build_campaign_plan


def run_matching(website_url: str = "", facebook_url: str = "",
                 raw_override: str = "", objective: str = None, top_k: int = 10,
                 weights: Dict[str, float] | None = None, plan: bool = False,
                 youtube_url: str = "", tiktok_url: str = "",
                 instagram_url: str = "", x_url: str = "",
                 platform_urls: Dict[str, str] | None = None) -> Dict:
    objective = objective or config.DEFAULT_OBJECTIVE
    brand: BrandProfile = analyze_brand(
        website_url=website_url,
        facebook_url=facebook_url,
        raw_override=raw_override,
        youtube_url=youtube_url,
        tiktok_url=tiktok_url,
        instagram_url=instagram_url,
        x_url=x_url,
        platform_urls=platform_urls,
    )
    terms = brand.to_query_terms() or [brand.industry]
    candidates: List[Dict] = get_candidate_kols(terms)
    scored = score_kols(brand, candidates, objective=objective, weights=weights)
    ranked = add_rationales(brand, scored["eligible"])
    output = {
        "brand": brand.to_dict(),
        "objective": objective,
        "objective_label": config.OBJECTIVES.get(objective, {}).get("label", objective),
        "search_terms": terms,
        "candidate_count": len(candidates),
        "eligible_count": len(scored["eligible"]),
        "results": ranked[:top_k],
        "excluded": scored["excluded"],
        "demo_mode": config.DEMO_MODE,
        "platform_count": len(brand.platform_contexts),
    }
    if plan:
        output["campaign_plan"] = build_campaign_plan(scored["eligible"], objective)
    return output


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="TikTok KOL Matcher")
    parser.add_argument("--website", default="")
    parser.add_argument("--facebook", default="")
    parser.add_argument("--youtube", default="")
    parser.add_argument("--tiktok", default="")
    parser.add_argument("--instagram", default="")
    parser.add_argument("--x", default="")
    parser.add_argument("--text", default="", help="Paste brand text instead of scraping")
    parser.add_argument("--objective", default=config.DEFAULT_OBJECTIVE,
                        choices=list(config.OBJECTIVES.keys()))
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--plan", action="store_true", help="Show full-funnel creator mix")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_matching(
        website_url=args.website,
        facebook_url=args.facebook,
        youtube_url=args.youtube,
        tiktok_url=args.tiktok,
        instagram_url=args.instagram,
        x_url=args.x,
        raw_override=args.text,
        objective=args.objective,
        top_k=args.top,
        plan=args.plan,
    )

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        brand = out["brand"]
        print("\\n=== BRAND PROFILE ===")
        print(f"  {brand['brand_name']} | industry: {brand['industry']} | objective: {out['objective_label']}")
        print(f"  demo={out['demo_mode']}, candidates={out['candidate_count']}, "
              f"eligible={out['eligible_count']}, platforms={out['platform_count']}")
        print("\\n=== PLATFORM CONTEXTS ===")
        for context in brand.get("platform_contexts", []):
            print(f"  {context['platform']}: {context['role']}")
        if out["excluded"]:
            print(f"\\n=== EXCLUDED BY GATES ({len(out['excluded'])}) ===")
            for excluded in out["excluded"]:
                print(f"  @{excluded['username']}: {', '.join(excluded['excluded_reasons'])}")
        print(f"\\n=== TOP {min(args.top, len(out['results']))} ELIGIBLE CREATORS ===")
        for index, row in enumerate(out["results"][:args.top], 1):
            print(f"\\n{index}. @{row['username']} [{row['tier']}] score={row['match_score']}")
            print(f"   {row['url']}")
            print(f"   ER={row['engagement_rate']}% sub={row['subscores']}")
            if row.get("rationale"):
                print(f"   -> {row['rationale']}")
