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
                 weights: Dict[str, float] | None = None, plan: bool = False) -> Dict:
    objective = objective or config.DEFAULT_OBJECTIVE
    brand: BrandProfile = analyze_brand(website_url, facebook_url, raw_override)
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
    parser.add_argument("--text", default="", help="Paste brand text instead of scraping")
    parser.add_argument("--objective", default=config.DEFAULT_OBJECTIVE,
                        choices=list(config.OBJECTIVES.keys()))
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--plan", action="store_true", help="Show full-funnel creator mix")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    out = run_matching(args.website, args.facebook, args.text,
                       objective=args.objective, top_k=args.top, plan=args.plan)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        brand = out["brand"]
        print("\n=== BRAND PROFILE ===")
        print(f"  {brand['brand_name']} | industry: {brand['industry']} | objective: {out['objective_label']}")
        print(f"  demo={out['demo_mode']}, candidates={out['candidate_count']}, eligible={out['eligible_count']}")
        if out["excluded"]:
            print(f"\n=== EXCLUDED BY GATES ({len(out['excluded'])}) ===")
            for excluded in out["excluded"]:
                print(f"  @{excluded['username']}: {', '.join(excluded['excluded_reasons'])}")
        print(f"\n=== TOP {min(args.top, len(out['results']))} ELIGIBLE CREATORS ===")
        for index, row in enumerate(out["results"][:args.top], 1):
            print(f"\n{index}. @{row['username']} [{row['tier']}] score={row['match_score']}")
            print(f"   {row['url']}")
            print(f"   ER={row['engagement_rate']}% sub={row['subscores']}")
            if row.get("rationale"):
                print(f"   -> {row['rationale']}")
        if out.get("campaign_plan"):
            plan = out["campaign_plan"]
            print(f"\n=== CAMPAIGN PLAN - {out['objective_label']} ===")
            print(f"  creators: {plan['total_creators']} | est reach: {plan['est_reach']:,} views | "
                  f"est budget: THB {plan['est_cost_lo']:,}-{plan['est_cost_hi']:,} (illustrative)")
            for slot in plan["buckets"]:
                names = ", ".join(f"@{creator['username']}" for creator in slot["creators"]) or "none"
                print(f"  [{slot['meta']['funnel']}] {slot['meta']['label']} "
                      f"({len(slot['creators'])}/{slot['target']}): {names}")
