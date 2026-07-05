"""Central configuration. Reads secrets from environment variables or .env."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

APIFY_TIKTOK_ACTOR = os.getenv("APIFY_TIKTOK_ACTOR", "clockworks/tiktok-scraper")
APIFY_FB_ACTOR = os.getenv("APIFY_FB_ACTOR", "apify/facebook-pages-scraper")

DEMO_MODE = os.getenv("DEMO_MODE", "1") == "1"

WEIGHTS = {
    "relevance": 0.25,
    "audience": 0.20,
    "objective": 0.20,
    "content_style": 0.15,
    "engagement": 0.10,
    "commerce": 0.05,
    "safety": 0.05,
}

RECENCY_MAX_DAYS = int(os.getenv("RECENCY_MAX_DAYS", "45"))
SAFETY_HARD_FLOOR = float(os.getenv("SAFETY_HARD_FLOOR", "0.35"))

OBJECTIVES = {
    "awareness": {
        "label": "Awareness",
        "prefer_roles": ["entertainer", "lifestyle", "storyteller", "reviewer"],
        "prefer_tiers": ["macro", "mega", "mid"],
        "needs_commerce": False,
    },
    "engagement": {
        "label": "Engagement",
        "prefer_roles": ["entertainer", "community", "storyteller", "lifestyle"],
        "prefer_tiers": ["micro", "mid", "macro"],
        "needs_commerce": False,
    },
    "leads": {
        "label": "Leads / Trust",
        "prefer_roles": ["educator", "expert", "reviewer", "community"],
        "prefer_tiers": ["nano", "micro", "mid"],
        "needs_commerce": False,
    },
    "sales": {
        "label": "Sales / Conversion",
        "prefer_roles": ["reviewer", "affiliate", "live_host", "educator"],
        "prefer_tiers": ["nano", "micro", "mid"],
        "needs_commerce": True,
    },
}

DEFAULT_OBJECTIVE = "awareness"
TOP_N_RATIONALE = int(os.getenv("TOP_N_RATIONALE", "5"))
