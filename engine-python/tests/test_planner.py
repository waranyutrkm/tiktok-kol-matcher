"""Tests for campaign planner creator mix."""
import os
os.environ["DEMO_MODE"] = "1"

from src.pipeline import run_matching
from src.planner import MIX_TARGETS


def _plan(objective):
    out = run_matching(raw_override="skincare cosmetics serum sensitive skin",
                       objective=objective, plan=True)
    return out["campaign_plan"]


def test_plan_has_expected_buckets_for_sales():
    plan = _plan("sales")
    keys = {bucket["meta"]["key"] for bucket in plan["buckets"]}
    assert {"conversion", "live"} <= keys


def test_no_creator_used_twice():
    plan = _plan("engagement")
    picked = [creator["username"] for bucket in plan["buckets"] for creator in bucket["creators"]]
    assert len(picked) == len(set(picked))


def test_conversion_bucket_only_has_commerce_creators():
    plan = _plan("sales")
    for bucket in plan["buckets"]:
        if bucket["meta"]["key"] == "conversion":
            for creator in bucket["creators"]:
                assert any(creator.get("commerce", {}).values())


def test_summary_fields_present():
    plan = _plan("awareness")
    assert plan["total_creators"] >= 1
    assert plan["est_cost_hi"] >= plan["est_cost_lo"] >= 0
    assert set(MIX_TARGETS["awareness"]) >= {bucket["meta"]["key"] for bucket in plan["buckets"]}
