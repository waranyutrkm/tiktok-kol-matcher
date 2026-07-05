"""Brand analysis step for the creator matching pipeline."""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from . import config


@dataclass
class PlatformContext:
    platform: str
    url: str = ""
    role: str = ""
    expected_signals: List[str] = field(default_factory=list)


@dataclass
class BrandProfile:
    brand_name: str = ""
    industry: str = ""
    products_services: List[str] = field(default_factory=list)
    target_audience: str = ""
    audience_age: str = ""
    audience_interests: List[str] = field(default_factory=list)
    brand_tone: str = ""
    content_themes: List[str] = field(default_factory=list)
    search_keywords: List[str] = field(default_factory=list)
    suggested_hashtags: List[str] = field(default_factory=list)
    platform_contexts: List[Dict] = field(default_factory=list)

    def to_query_terms(self) -> List[str]:
        terms = []
        terms += self.products_services
        terms += self.content_themes
        terms += self.audience_interests
        terms += self.search_keywords
        terms += [self.industry]
        for context in self.platform_contexts:
            terms += context.get("expected_signals", [])
        return [term.strip().lower() for term in terms if term and term.strip()]

    def as_text(self) -> str:
        platform_text = " ".join(
            f"{context.get('platform','')} {context.get('role','')} "
            f"{' '.join(context.get('expected_signals', []))}"
            for context in self.platform_contexts
        )
        return (
            f"{self.brand_name} {self.industry} "
            f"{' '.join(self.products_services)} {self.target_audience} "
            f"{' '.join(self.audience_interests)} {' '.join(self.content_themes)} "
            f"{' '.join(self.search_keywords)} {platform_text}"
        )

    def to_dict(self):
        return asdict(self)


PLATFORM_RESEARCH_MAP = {
    "website": {
        "role": "owned positioning and conversion context",
        "expected_signals": ["product pages", "pricing", "claims", "proof points", "SEO intent"],
    },
    "facebook": {
        "role": "community trust and long-copy storytelling",
        "expected_signals": ["comments", "reviews", "local trust", "community questions", "long-form posts"],
    },
    "youtube": {
        "role": "long-form education and script depth",
        "expected_signals": ["transcripts", "chapters", "retention hooks", "tutorial structure", "expert framing"],
    },
    "tiktok": {
        "role": "short-form hooks and scene-native storytelling",
        "expected_signals": ["opening hook", "scene beats", "caption style", "CTA rhythm", "creator language"],
    },
    "instagram": {
        "role": "visual identity and lifestyle framing",
        "expected_signals": ["reels", "story highlights", "visual codes", "aesthetic consistency", "social proof"],
    },
    "x": {
        "role": "real-time conversation and risk context",
        "expected_signals": ["topic velocity", "opinion framing", "reply risk", "concise messaging", "controversy signals"],
    },
}


def build_platform_contexts(platform_urls: Dict[str, str]) -> List[Dict]:
    contexts = []
    for platform, url in platform_urls.items():
        url = (url or "").strip()
        if not url:
            continue
        meta = PLATFORM_RESEARCH_MAP.get(platform, {})
        contexts.append(asdict(PlatformContext(
            platform=platform,
            url=url,
            role=meta.get("role", "brand channel context"),
            expected_signals=meta.get("expected_signals", []),
        )))
    return contexts


def fetch_website_text(url: str, max_chars: int = 6000) -> str:
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0 (compatible; KOLMatcher/1.0)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    title = (soup.title.string if soup.title else "") or ""
    desc = ""
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        desc = md["content"]
    return (f"{title}. {desc}. " + text)[:max_chars]


def fetch_facebook_text(fb_url: str, max_chars: int = 3000) -> str:
    if config.DEMO_MODE or not config.APIFY_TOKEN:
        return ""
    try:
        from apify_client import ApifyClient
        client = ApifyClient(config.APIFY_TOKEN)
        run = client.actor(config.APIFY_FB_ACTOR).call(
            run_input={"startUrls": [{"url": fb_url}], "resultsLimit": 1}
        )
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        if not items:
            return ""
        page = items[0]
        parts = [page.get("title", ""), page.get("intro", ""), page.get("info", ""),
                 " ".join(page.get("categories", []) or [])]
        return " ".join(x for x in parts if x)[:max_chars]
    except Exception as exc:
        print(f"[brand_analyzer] Facebook fetch skipped: {exc}")
        return ""


_LLM_PROMPT = """You are a marketing analyst. Extract a structured brand profile
for creator matching from the raw brief and platform context below.
Return ONLY valid JSON with these keys:
brand_name, industry, products_services (list), target_audience (string),
audience_age, audience_interests (list), brand_tone, content_themes (list),
search_keywords (list), suggested_hashtags (list).
Use English for every value.

RAW TEXT AND PLATFORM CONTEXT:
\"\"\"{raw}\"\"\"
"""


def _llm_profile(raw: str, platform_contexts: List[Dict]) -> BrandProfile | None:
    if config.DEMO_MODE or not config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": _LLM_PROMPT.format(raw=raw[:8000])}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        data = json.loads(resp.choices[0].message.content)
        profile = BrandProfile(**{k: data.get(k, BrandProfile().__dict__[k])
                                  for k in BrandProfile().__dict__ if k != "platform_contexts"})
        profile.platform_contexts = platform_contexts
        return profile
    except Exception as exc:
        print(f"[brand_analyzer] LLM profile failed, using heuristic: {exc}")
        return None


_CATEGORY_BANK = {
    "beauty": ["skincare", "cosmetics", "serum", "sensitive skin", "clean beauty", "beauty"],
    "food": ["food", "restaurant", "cafe", "delivery", "street food", "dining"],
    "tech": ["smartphone", "gadget", "laptop", "computer", "technology", "software"],
    "fashion": ["fashion", "clothing", "style", "outfit", "shopping", "ootd"],
    "fitness": ["fitness", "health", "gym", "supplement", "nutrition", "wellness"],
    "finance": ["finance", "investing", "saving", "budgeting", "insurance", "wealth"],
    "home": ["home", "decor", "furniture", "condo", "organization", "interior"],
    "parenting": ["parenting", "baby", "kids", "family", "motherhood", "childcare"],
    "travel": ["travel", "hotel", "trip", "destination", "tourism", "resort"],
    "pet": ["pet", "dog", "cat", "pet food", "grooming", "pet care"],
}


def _heuristic_profile(raw: str, url: str, platform_contexts: List[Dict]) -> BrandProfile:
    low = raw.lower()
    scores = {cat: sum(low.count(word.lower()) for word in words)
              for cat, words in _CATEGORY_BANK.items()}
    best = max(scores, key=scores.get) if any(scores.values()) else "lifestyle"
    words = re.findall(r"[a-zA-Z]{3,}", low)
    common = [word for word, _ in Counter(words).most_common(15)]
    brand = re.sub(r"^https?://(www\\.)?", "", url).split("/")[0].split(".")[0]
    bank = _CATEGORY_BANK.get(best, [])
    return BrandProfile(
        brand_name=brand.title() if brand else "Demo Brand",
        industry=best,
        products_services=bank[:4],
        target_audience=f"Consumers interested in {best}",
        audience_age="18-40",
        audience_interests=bank[:5],
        brand_tone="friendly, trustworthy",
        content_themes=bank[:4],
        search_keywords=common[:8] or bank[:5],
        suggested_hashtags=[f"#{word.replace(' ', '')}" for word in bank[:5]],
        platform_contexts=platform_contexts,
    )


def analyze_brand(website_url: str = "", facebook_url: str = "",
                  raw_override: str = "", youtube_url: str = "",
                  tiktok_url: str = "", instagram_url: str = "",
                  x_url: str = "", platform_urls: Dict[str, str] | None = None) -> BrandProfile:
    urls = {
        "website": website_url,
        "facebook": facebook_url,
        "youtube": youtube_url,
        "tiktok": tiktok_url,
        "instagram": instagram_url,
        "x": x_url,
    }
    if platform_urls:
        urls.update(platform_urls)
    platform_contexts = build_platform_contexts(urls)

    if raw_override:
        raw = raw_override
    else:
        raw = ""
        if website_url and not config.DEMO_MODE:
            try:
                raw += fetch_website_text(website_url)
            except Exception as exc:
                print(f"[brand_analyzer] website fetch failed: {exc}")
        raw += " " + fetch_facebook_text(facebook_url)

    context_text = " ".join(
        f"{ctx['platform']} url={ctx['url']} role={ctx['role']} signals={' '.join(ctx['expected_signals'])}"
        for ctx in platform_contexts
    )
    raw = f"{raw} {context_text}".strip()
    if not raw:
        raw = next((url for url in urls.values() if url), "brand")

    profile = _llm_profile(raw, platform_contexts)
    if profile is None:
        profile = _heuristic_profile(raw, next((url for url in urls.values() if url), "brand"), platform_contexts)
    return profile
