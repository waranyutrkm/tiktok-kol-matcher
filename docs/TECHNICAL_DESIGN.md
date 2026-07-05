# Technical Design

TikTok KOL Matcher is structured as a small creator recommendation pipeline.

## Pipeline

```text
Brand input
-> Brand profile extraction
-> Candidate creator retrieval
-> Eligibility gates
-> Weighted scoring
-> Rationale generation
-> Ranked shortlist
-> Campaign planner
```

## Components

### Brand Analyzer

Turns website text, social profile text, or manual brief text into a structured brand profile.

### KOL Fetcher

Returns candidate creators. In demo mode it loads `data/demo_kols.json`. In live mode it can be adapted to approved APIs or data providers.

### Matcher

Runs hard eligibility gates first, then scores only eligible creators with the 7-factor model.

### Planner

Groups ranked creators into a full-funnel campaign mix such as awareness, trust building, review burst, conversion, and live commerce.

## Design Principles

- Keep ranking logic explainable
- Make data-source adapters replaceable
- Separate scoring from rationale writing
- Keep demo mode fully offline
- Keep secrets out of git
