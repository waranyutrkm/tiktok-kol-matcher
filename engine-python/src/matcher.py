"""Score and rank candidate creators against a brand profile."""
from __future__ import annotations

import math
import re
from typing import Dict, List, Tuple

from . import config
from .brand_analyzer import BrandProfile


def _tokens(text: str) -> List[str]:
    text = (text or "").lower()
    latin = re.findall(r"[a-z0-9]{2,}", text)
    thai_runs = re.findall(r"[\u0E00-\u0E7F]{2,}", text)
    grams = []
    for run in thai_runs:
        grams.append(run)
        for i in range(0, max(1, len(run) - 2)):
            grams.append(run[i:i + 3])
    return latin + grams


def _bow(tokens: List[str]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for token in tokens:
        out[token] = out.get(token, 0.0) + 1.0
    return out


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    numerator = sum(a[t] * b[t] for t in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return numerator / (da * db) if da and db else 0.0


def _tier(followers: int) -> str:
    if followers < 10_000:
        return "nano"
    if followers < 100_000:
        return "micro"
    if followers < 500_000:
        return "mid"
    if followers < 1_000_000:
        return "macro"
    return "mega"


def _relevance(brand: BrandProfile, kol: Dict) -> float:
    brand_bow = _bow(_tokens(brand.as_text() + " " + " ".join(brand.suggested_hashtags)))
    kol_text = " ".join([kol.get("bio", ""), kol.get("nickname", ""),
                         " ".join(kol.get("categories", [])),
                         " ".join(kol.get("recent_hashtags", []))])
    return min(1.0, _cosine(brand_bow, _bow(_tokens(kol_text))) * 2.2)


def _content_style(brand: BrandProfile, kol: Dict) -> float:
    brand_bow = _bow(_tokens(" ".join(brand.content_themes) + " " +
                             " ".join(brand.suggested_hashtags)))
    kol_bow = _bow(_tokens(" ".join(kol.get("recent_hashtags", [])) + " " +
                           " ".join(kol.get("roles", []))))
    return min(1.0, _cosine(brand_bow, kol_bow) * 2.5)


def _engagement(kol: Dict) -> float:
    views = max(1, kol.get("avg_views", 0))
    interactions = kol.get("avg_likes", 0) + kol.get("avg_comments", 0) * 3 + kol.get("avg_shares", 0) * 2
    return max(0.0, min(1.0, (interactions / views) / 0.15))


def _audience(brand: BrandProfile, kol: Dict) -> float:
    score = 0.0
    if kol.get("region", "").upper() == "TH":
        score += 0.6
    if kol.get("language", "").lower() == "th":
        score += 0.4
    if not kol.get("region") and not kol.get("language"):
        score = 0.5
    return min(1.0, score)


def _objective_fit(kol: Dict, objective: str) -> float:
    obj = config.OBJECTIVES.get(objective, config.OBJECTIVES[config.DEFAULT_OBJECTIVE])
    roles = set(kol.get("roles", []))
    commerce = kol.get("commerce", {})
    if commerce.get("affiliate"):
        roles.add("affiliate")
    if commerce.get("live_host"):
        roles.add("live_host")

    score = 0.0
    preferred = set(obj["prefer_roles"])
    if roles & preferred:
        score += 0.6 * min(1.0, len(roles & preferred) / 2)
    if _tier(kol.get("followers", 0)) in obj["prefer_tiers"]:
        score += 0.25
    score += 0.15 if (not obj["needs_commerce"] or any(commerce.values())) else 0.0
    return min(1.0, score)


def _commerce(kol: Dict) -> float:
    commerce = kol.get("commerce", {})
    return min(1.0, 0.40 * bool(commerce.get("affiliate")) +
                    0.35 * bool(commerce.get("shop")) +
                    0.25 * bool(commerce.get("live_host")))


def _safety(kol: Dict) -> float:
    score = 0.5
    if kol.get("verified"):
        score += 0.2
    followers = max(1, kol.get("followers", 0))
    like_ratio = kol.get("avg_likes", 0) / followers
    if 0.02 <= like_ratio <= 0.5:
        score += 0.3
    return min(1.0, score)


def eligibility_gates(kol: Dict, objective: str) -> Tuple[bool, List[str]]:
    reasons = []
    if not kol.get("is_public", True):
        reasons.append("Profile is not public")
    if kol.get("region", "").upper() != "TH" and kol.get("language", "").lower() != "th":
        reasons.append("Market or language signal does not match")
    if kol.get("last_post_days", 0) > config.RECENCY_MAX_DAYS:
        reasons.append(f"No recent post within {config.RECENCY_MAX_DAYS} days")
    if _safety(kol) < config.SAFETY_HARD_FLOOR:
        reasons.append("Brand-safety signal is below threshold")
    obj = config.OBJECTIVES.get(objective, {})
    if obj.get("needs_commerce") and not any(kol.get("commerce", {}).values()):
        reasons.append("Sales objective requires a commerce signal")
    return (len(reasons) == 0, reasons)


def score_kols(brand: BrandProfile, kols: List[Dict], objective: str = None,
               weights: Dict[str, float] | None = None) -> Dict[str, List[Dict]]:
    objective = objective or config.DEFAULT_OBJECTIVE
    weights = weights or config.WEIGHTS
    weight_sum = sum(weights.values()) or 1.0

    eligible, excluded = [], []
    for kol in kols:
        ok, reasons = eligibility_gates(kol, objective)
        if not ok:
            excluded.append({**kol, "tier": _tier(kol.get("followers", 0)),
                             "excluded_reasons": reasons})
            continue
        subs = {
            "relevance": _relevance(brand, kol),
            "audience": _audience(brand, kol),
            "objective": _objective_fit(kol, objective),
            "content_style": _content_style(brand, kol),
            "engagement": _engagement(kol),
            "commerce": _commerce(kol),
            "safety": _safety(kol),
        }
        total = sum(subs[k] * weights.get(k, 0) for k in subs) / weight_sum
        er = (kol.get("avg_likes", 0) + kol.get("avg_comments", 0)
              + kol.get("avg_shares", 0)) / max(1, kol.get("avg_views", 0))
        eligible.append({
            **kol,
            "match_score": round(total * 100, 1),
            "subscores": {k: round(v * 100, 1) for k, v in subs.items()},
            "engagement_rate": round(er * 100, 2),
            "tier": _tier(kol.get("followers", 0)),
            "objective": objective,
        })
    eligible.sort(key=lambda x: x["match_score"], reverse=True)
    return {"eligible": eligible, "excluded": excluded}


def add_rationales(brand: BrandProfile, ranked: List[Dict],
                   top_n: int | None = None) -> List[Dict]:
    top_n = top_n or config.TOP_N_RATIONALE
    if config.DEMO_MODE or not config.OPENAI_API_KEY:
        for row in ranked[:top_n]:
            row["rationale"] = _template_rationale(brand, row)
        return ranked
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        for row in ranked[:top_n]:
            prompt = (
                f"Brand: {brand.brand_name} ({brand.industry}). "
                f"Objective: {row.get('objective')}. Audience: {brand.target_audience}. "
                f"Creator: @{row['username']} - {row.get('bio','')}, roles={row.get('roles')}, "
                f"commerce={row.get('commerce')}. Match {row['match_score']}, ER "
                f"{row['engagement_rate']}%, tier {row['tier']}. Explain the fit in two concise English sentences."
            )
            resp = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4)
            row["rationale"] = resp.choices[0].message.content.strip()
    except Exception as exc:
        print(f"[matcher] LLM rationale failed, using template: {exc}")
        for row in ranked[:top_n]:
            row.setdefault("rationale", _template_rationale(brand, row))
    return ranked


def _template_rationale(brand: BrandProfile, row: Dict) -> str:
    subs = row["subscores"]
    strongest = max(subs, key=subs.get)
    label = {
        "relevance": "strong brand-content relevance",
        "audience": "strong market and language fit",
        "objective": "strong campaign-objective fit",
        "content_style": "compatible content style",
        "engagement": "high engagement quality",
        "commerce": "commerce readiness",
        "safety": "credible profile signals",
    }[strongest]
    commerce = row.get("commerce", {})
    caps = [key for key, value in commerce.items() if value]
    cap_text = f" Commerce signals: {', '.join(caps)}." if caps else ""
    return (f"@{row['username']} is recommended for {label}. "
            f"Relevance {subs['relevance']}, objective fit {subs['objective']}, "
            f"and ER {row['engagement_rate']}%.{cap_text} "
            f"Confidence is {row.get('data_confidence','estimated')}; human review is recommended.")
