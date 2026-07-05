# TikTok KOL Matcher

An open, reusable prototype for matching brands with relevant TikTok creators.

The project is intentionally generic. It is not tied to any agency, client, hiring process, or private brand. Teams can fork it, replace the demo data, connect their own data sources, and adapt the scoring model for their influencer marketing workflow.

## What It Does

- Accepts a brand brief, website URL, or social profile URL as input
- Builds a structured brand profile
- Retrieves candidate creators from a demo creator pool or live data adapter
- Applies eligibility gates before ranking
- Scores creators with an explainable 7-factor model
- Returns clickable TikTok profile links
- Produces a campaign planning view for creator mix design
- Includes a Python engine, tests, and a browser-based demo

## Quick Start

### Browser Demo

Open `index.html` in a browser and click `Run skincare demo`.

No installation is required for the browser demo.

### Python Engine

```bash
cd engine-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

The engine runs in demo mode by default and does not require API keys.

To use live data adapters:

```bash
cp .env.example .env
```

Then set the relevant values:

```bash
DEMO_MODE=0
OPENAI_API_KEY=your_openai_key
APIFY_TOKEN=your_apify_token
```

Keep real secrets in `.env` only. The `.env` file is ignored by git.

## Matching Model

Creators must pass eligibility gates before scoring:

- Public profile
- Target market and language fit
- Recent activity
- No severe brand-safety risk
- Objective compatibility, such as commerce capability for sales campaigns

Eligible creators are scored across seven factors:

| Factor | Weight |
| --- | ---: |
| Brand relevance | 25 |
| Audience fit | 20 |
| Objective fit | 20 |
| Content style match | 15 |
| Performance quality | 10 |
| Commerce capability | 5 |
| Brand safety and professionalism | 5 |

Performance quality uses view-based engagement rate:

```text
(likes + comments + shares) / views * 100
```

The scoring layer is deliberately explainable. LLMs can be used for profile extraction and rationale writing, but the ranking logic remains inspectable and adjustable.

## Project Structure

```text
tiktok-kol-matcher/
├── index.html
├── README.md
├── docs/
│   ├── DEMO_WALKTHROUGH.md
│   ├── RESEARCH_NOTES.md
│   ├── ROADMAP.md
│   └── TECHNICAL_DESIGN.md
└── engine-python/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── data/demo_kols.json
    ├── src/
    │   ├── brand_analyzer.py
    │   ├── kol_fetcher.py
    │   ├── matcher.py
    │   ├── planner.py
    │   └── pipeline.py
    └── tests/
        ├── test_matcher.py
        ├── test_pipeline.py
        └── test_planner.py
```

## Data Scope

The bundled creator data is synthetic and exists only to demonstrate the workflow. It is not a real creator database.

For production use, replace the demo pool with authorized data sources, internal CRM data, first-party campaign results, or approved public-data providers.

## Ethics And Privacy

This project should be used as an assisted recommendation system, not an automated hiring or exclusion tool.

Recommended safeguards:

- Use public or authorized data sources only
- Keep data retention policies explicit
- Avoid storing unnecessary personal data
- Show confidence levels for estimated audience signals
- Keep humans in the final decision loop
- Provide explanations for every recommendation and exclusion

## License

MIT
