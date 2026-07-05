# Python Engine

This folder contains the reusable matching engine behind the browser demo.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

## Demo Mode

The engine runs in demo mode by default. It loads synthetic creator data from:

```text
data/demo_kols.json
```

No API keys are required in demo mode.

## Live Mode

Copy the environment template:

```bash
cp .env.example .env
```

Set `DEMO_MODE=0` and add the API keys required by your adapters.

## Modules

- `src/brand_analyzer.py` builds a structured brand profile.
- `src/kol_fetcher.py` retrieves candidate creators.
- `src/matcher.py` applies eligibility gates and weighted scoring.
- `src/planner.py` builds a full-funnel creator mix.
- `src/pipeline.py` orchestrates the end-to-end flow.
