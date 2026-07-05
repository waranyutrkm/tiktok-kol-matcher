# Project Map

```text
engine-python/
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

The engine is designed so data collection, scoring, and presentation can be developed independently.
