"""End-to-end pipeline tests in demo mode."""
import os
os.environ["DEMO_MODE"] = "1"

from src.pipeline import run_matching


def test_end_to_end_returns_results():
    out = run_matching(raw_override="laptop gadget computer store",
                       objective="awareness", top_k=5)
    assert out["demo_mode"] is True
    assert out["candidate_count"] > 0
    assert 1 <= len(out["results"]) <= 5
    first = out["results"][0]
    assert {"username", "url", "match_score", "engagement_rate", "tier",
            "subscores"} <= set(first)
    assert {"relevance", "audience", "objective", "content_style",
            "engagement", "commerce", "safety"} <= set(first["subscores"])


def test_tech_brand_surfaces_tech_creator():
    out = run_matching(raw_override="smartphone gadget laptop technology review",
                       objective="leads", top_k=3)
    usernames = {row["username"] for row in out["results"]}
    assert "techsanook" in usernames


def test_sales_objective_changes_shortlist():
    sales = run_matching(raw_override="skincare cosmetics serum",
                         objective="sales", top_k=10)
    for row in sales["results"]:
        assert any(row.get("commerce", {}).values())


def test_excluded_list_has_reasons():
    out = run_matching(raw_override="skincare serum", objective="awareness")
    for row in out["excluded"]:
        assert row["excluded_reasons"]
