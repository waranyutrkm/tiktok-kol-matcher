"""Unit tests for the core matching logic. Run in demo mode."""
import os
os.environ["DEMO_MODE"] = "1"

from src.brand_analyzer import analyze_brand
from src.kol_fetcher import get_candidate_kols
from src.matcher import score_kols, _engagement, _relevance, eligibility_gates


def _beauty_brand():
    return analyze_brand(raw_override="clean skincare cosmetics serum for sensitive skin women 18-35")


def _ranked(objective="awareness"):
    brand = _beauty_brand()
    return score_kols(brand, get_candidate_kols(["skincare"]), objective=objective)


def test_scores_within_bounds():
    for row in _ranked()["eligible"]:
        assert 0 <= row["match_score"] <= 100
        for value in row["subscores"].values():
            assert 0 <= value <= 100


def test_beauty_brand_ranks_beauty_creators_on_top():
    top2 = {row["username"] for row in _ranked()["eligible"][:2]}
    assert top2 & {"beautybowljidapa", "cleanbeautymild"}, top2


def test_engagement_rewards_high_interaction_rate():
    high = {"avg_views": 100, "avg_likes": 15, "avg_comments": 0, "avg_shares": 0}
    low = {"avg_views": 100, "avg_likes": 1, "avg_comments": 0, "avg_shares": 0}
    assert _engagement(high) > _engagement(low)


def test_relevance_discriminates_by_topic():
    brand = _beauty_brand()
    beauty = {"bio": "skincare cosmetics serum beauty", "categories": ["beauty"],
              "recent_hashtags": ["#skincare"], "nickname": "beauty"}
    finance = {"bio": "finance investing saving stocks", "categories": ["finance"],
               "recent_hashtags": ["#investing"], "nickname": "finance"}
    assert _relevance(brand, beauty) > _relevance(brand, finance)


def test_output_has_tiktok_url():
    assert all(row["url"].startswith("https://www.tiktok.com/@")
               for row in _ranked()["eligible"])


def test_ranking_is_sorted_descending():
    scores = [row["match_score"] for row in _ranked()["eligible"]]
    assert scores == sorted(scores, reverse=True)


def test_stale_creator_is_excluded_by_recency_gate():
    excluded = {row["username"] for row in _ranked()["excluded"]}
    assert "gadgetgeekttp" in excluded


def test_sales_objective_requires_commerce_signal():
    brand = _beauty_brand()
    out = score_kols(brand, get_candidate_kols(["skincare"]), objective="sales")
    excluded = {row["username"] for row in out["excluded"]}
    assert "travelgorn" in excluded


def test_gate_returns_reasons():
    ok, reasons = eligibility_gates(
        {"is_public": True, "region": "TH", "language": "th",
         "last_post_days": 999, "verified": True, "followers": 10000,
         "avg_likes": 500, "commerce": {}}, "awareness")
    assert ok is False and any("recent" in reason for reason in reasons)
