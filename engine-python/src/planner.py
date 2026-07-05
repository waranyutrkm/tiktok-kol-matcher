"""Build a full-funnel creator mix from ranked creators."""
from __future__ import annotations

from typing import Dict, List


BUCKETS = [
    {"key": "awareness", "label": "Awareness / Reach", "funnel": "Awareness",
     "roles": {"entertainer", "lifestyle", "storyteller", "reviewer"},
     "commerce": None, "tiers": {"mid", "macro", "mega"},
     "note": "Build broad awareness and reach."},
    {"key": "trust", "label": "Trust-building educator", "funnel": "Consideration",
     "roles": {"educator", "expert"}, "commerce": None,
     "tiers": {"nano", "micro", "mid"},
     "note": "Explain the category and build credibility before purchase."},
    {"key": "review", "label": "Review burst", "funnel": "Consideration",
     "roles": {"reviewer", "community"}, "commerce": None,
     "tiers": {"nano", "micro", "mid"},
     "note": "Create practical social proof through product reviews."},
    {"key": "conversion", "label": "Conversion affiliate/shop", "funnel": "Conversion",
     "roles": None, "commerce": {"affiliate", "shop"}, "tiers": None,
     "note": "Support measurable conversion through affiliate or shop mechanics."},
    {"key": "live", "label": "Live commerce peak", "funnel": "Conversion",
     "roles": None, "commerce": {"live_host"}, "tiers": None,
     "note": "Create a focused selling moment during the campaign."},
]

MIX_TARGETS = {
    "awareness":  {"awareness": 3, "trust": 1, "review": 3, "conversion": 1, "live": 0},
    "engagement": {"awareness": 2, "trust": 1, "review": 3, "conversion": 1, "live": 1},
    "leads":      {"awareness": 0, "trust": 4, "review": 2, "conversion": 1, "live": 0},
    "sales":      {"awareness": 0, "trust": 1, "review": 2, "conversion": 4, "live": 2},
}

RATE_CARD = {
    "nano":  (1_500, 3_000),
    "micro": (5_000, 15_000),
    "mid":   (20_000, 50_000),
    "macro": (60_000, 150_000),
    "mega":  (150_000, 400_000),
}


def _qualifies(kol: Dict, bucket: Dict) -> bool:
    roles = set(kol.get("roles", []))
    commerce = kol.get("commerce", {})
    if commerce.get("affiliate"):
        roles.add("affiliate")
    if commerce.get("live_host"):
        roles.add("live_host")
    if bucket["roles"] is not None and not (roles & bucket["roles"]):
        return False
    if bucket["commerce"] is not None and not any(commerce.get(c) for c in bucket["commerce"]):
        return False
    if bucket["tiers"] is not None and kol.get("tier") not in bucket["tiers"]:
        return False
    return True


def build_campaign_plan(eligible: List[Dict], objective: str) -> Dict:
    targets = MIX_TARGETS.get(objective, MIX_TARGETS["awareness"])
    active = [bucket for bucket in BUCKETS if targets.get(bucket["key"], 0) > 0]
    plan = {bucket["key"]: {"meta": bucket, "target": targets[bucket["key"]], "creators": []}
            for bucket in active}

    used = set()
    scarcity = sorted(active, key=lambda bucket: sum(1 for kol in eligible if _qualifies(kol, bucket)))
    for bucket in scarcity:
        slot = plan[bucket["key"]]
        for kol in eligible:
            if kol["username"] in used:
                continue
            if len(slot["creators"]) < slot["target"] and _qualifies(kol, bucket):
                slot["creators"].append(kol)
                used.add(kol["username"])

    all_picked = [creator for slot in plan.values() for creator in slot["creators"]]
    total_reach = sum(c.get("avg_views", 0) or c.get("followers", 0) for c in all_picked)
    cost_lo = sum(RATE_CARD.get(c["tier"], (0, 0))[0] for c in all_picked)
    cost_hi = sum(RATE_CARD.get(c["tier"], (0, 0))[1] for c in all_picked)
    for slot in plan.values():
        creators = slot["creators"]
        slot["reach"] = sum(c.get("avg_views", 0) or c.get("followers", 0) for c in creators)
        slot["cost_lo"] = sum(RATE_CARD.get(c["tier"], (0, 0))[0] for c in creators)
        slot["cost_hi"] = sum(RATE_CARD.get(c["tier"], (0, 0))[1] for c in creators)

    return {
        "objective": objective,
        "buckets": [plan[bucket["key"]] for bucket in active],
        "total_creators": len(all_picked),
        "est_reach": total_reach,
        "est_cost_lo": cost_lo,
        "est_cost_hi": cost_hi,
        "unfilled": {bucket["key"]: max(0, plan[bucket["key"]]["target"] - len(plan[bucket["key"]]["creators"]))
                     for bucket in active},
    }
