"""Streamlit dashboard for TikTok KOL Matcher."""
import pandas as pd
import streamlit as st

from src import config
from src.pipeline import run_matching


st.set_page_config(page_title="TikTok KOL Matcher", page_icon="KM", layout="wide")

st.title("TikTok KOL Matcher")
st.caption("Generic platform-aware creator discovery and campaign planning prototype")

mode_badge = "DEMO mode: bundled synthetic data" if config.DEMO_MODE else "LIVE mode: external adapters enabled"
st.info(mode_badge)

with st.expander("How to use this dashboard", expanded=False):
    st.markdown("""
1. Choose a campaign objective.
2. Add every available brand channel: website, Facebook, YouTube, TikTok, Instagram, and X.
3. Paste a brand brief.
4. Run matching.
5. Review platform context, score breakdowns, exclusions, and the campaign plan.

Each platform should be analyzed separately in production because storytelling conventions differ by channel.
""")

with st.sidebar:
    st.header("Scoring weights")
    weights = {
        "relevance": st.slider("Brand relevance", 0.0, 1.0, config.WEIGHTS["relevance"], 0.05),
        "audience": st.slider("Audience fit", 0.0, 1.0, config.WEIGHTS["audience"], 0.05),
        "objective": st.slider("Objective fit", 0.0, 1.0, config.WEIGHTS["objective"], 0.05),
        "content_style": st.slider("Content style", 0.0, 1.0, config.WEIGHTS["content_style"], 0.05),
        "engagement": st.slider("Performance quality", 0.0, 1.0, config.WEIGHTS["engagement"], 0.05),
        "commerce": st.slider("Commerce capability", 0.0, 1.0, config.WEIGHTS["commerce"], 0.05),
        "safety": st.slider("Brand safety", 0.0, 1.0, config.WEIGHTS["safety"], 0.05),
    }
    st.header("Display filters")
    tier_filter = st.multiselect("Creator tier", ["nano", "micro", "mid", "macro", "mega"],
                                 default=["nano", "micro", "mid", "macro", "mega"])
    min_followers = st.number_input("Minimum followers", 0, value=0, step=10000)
    top_k = st.slider("Creators to show", 3, 12, 8)

objective = st.radio("Campaign objective", list(config.OBJECTIVES.keys()), horizontal=True,
                     format_func=lambda key: config.OBJECTIVES[key]["label"])
planner_mode = st.toggle("Build campaign plan", value=True)

url_cols = st.columns(3)
website = url_cols[0].text_input("Website URL", placeholder="https://brand.com")
facebook = url_cols[1].text_input("Facebook URL", placeholder="https://facebook.com/brand")
youtube = url_cols[2].text_input("YouTube URL", placeholder="https://youtube.com/@brand")
url_cols2 = st.columns(3)
tiktok = url_cols2[0].text_input("TikTok URL", placeholder="https://tiktok.com/@brand")
instagram = url_cols2[1].text_input("Instagram URL", placeholder="https://instagram.com/brand")
x_url = url_cols2[2].text_input("X URL", placeholder="https://x.com/brand")

raw = st.text_area("Brand brief", placeholder="Example: clean skincare brand for sensitive-skin consumers aged 18-35")

if st.button("Find matching creators", type="primary", use_container_width=True):
    with st.spinner("Analyzing platform context and ranking creators"):
        st.session_state["out"] = run_matching(
            website_url=website,
            facebook_url=facebook,
            youtube_url=youtube,
            tiktok_url=tiktok,
            instagram_url=instagram,
            x_url=x_url,
            raw_override=raw,
            objective=objective,
            top_k=12,
            weights=weights,
            plan=planner_mode,
        )

out = st.session_state.get("out")
if not out:
    st.stop()

results = [row for row in out["results"]
           if row["tier"] in tier_filter and row["followers"] >= min_followers][:top_k]
brand = out["brand"]

st.subheader("Brand profile")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Candidates scanned", out["candidate_count"])
c2.metric("Platforms", out["platform_count"])
c3.metric("Eligible creators", out["eligible_count"])
c4.metric("Top score", results[0]["match_score"] if results else 0)
st.write({
    "brand_name": brand["brand_name"],
    "industry": brand["industry"],
    "target_audience": brand["target_audience"],
    "search_terms": out["search_terms"][:12],
})

with st.expander("Platform context"):
    for context in brand.get("platform_contexts", []):
        st.markdown(f"**{context['platform']}** - {context['role']}")
        st.caption(", ".join(context.get("expected_signals", [])))

if out["excluded"]:
    with st.expander("Excluded creators"):
        for row in out["excluded"]:
            st.write(f"@{row['username']}: {', '.join(row['excluded_reasons'])}")

if out.get("campaign_plan"):
    st.subheader("Campaign plan")
    plan = out["campaign_plan"]
    p1, p2, p3 = st.columns(3)
    p1.metric("Creators", plan["total_creators"])
    p2.metric("Estimated reach", f"{plan['est_reach']:,}")
    p3.metric("Estimated budget", f"THB {plan['est_cost_lo']:,}-{plan['est_cost_hi']:,}")
    for slot in plan["buckets"]:
        with st.container(border=True):
            st.markdown(f"**{slot['meta']['label']}** - {slot['meta']['funnel']}")
            st.caption(slot["meta"]["note"])
            for creator in slot["creators"]:
                st.markdown(f"[@{creator['username']}]({creator['url']}) - {creator['tier']} - score {creator['match_score']}")

st.subheader("Ranked creators")
subscore_keys = ["relevance", "audience", "objective", "content_style", "engagement", "commerce", "safety"]
for index, row in enumerate(results, 1):
    with st.container(border=True):
        st.markdown(f"### {index}. [@{row['username']}]({row['url']})")
        st.caption(f"{row.get('nickname','')} | {row['tier']} | {row['followers']:,} followers | ER {row['engagement_rate']}%")
        st.write(row.get("bio", ""))
        st.info(row.get("rationale", "No rationale available."))
        score_col, follower_col = st.columns(2)
        score_col.metric("Match score", row["match_score"])
        follower_col.metric("Followers", f"{row['followers']:,}")
        for key in subscore_keys:
            st.progress(min(1.0, row["subscores"][key] / 100), text=f"{key}: {row['subscores'][key]}")

df = pd.DataFrame([{
    "rank": index + 1,
    "username": row["username"],
    "url": row["url"],
    "objective": out["objective"],
    "match_score": row["match_score"],
    "followers": row["followers"],
    "engagement_rate_pct": row["engagement_rate"],
    "tier": row["tier"],
    "data_confidence": row.get("data_confidence", ""),
    **{key: row["subscores"][key] for key in subscore_keys},
} for index, row in enumerate(results)])
st.download_button("Download shortlist CSV", df.to_csv(index=False), "kol_shortlist.csv", "text/csv")
