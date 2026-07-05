# Technical Design

TikTok KOL Matcher is structured as a platform-aware creator recommendation pipeline.

## Pipeline

```text
Brand brief and platform URLs
-> Platform-specific ingestion
-> Script, caption, comment, and scene-beat extraction
-> Brand profile and platform context synthesis
-> Candidate creator retrieval
-> Eligibility gates
-> Weighted scoring
-> Rationale generation
-> Ranked shortlist
-> Campaign planner
```

## Platform Context Model

The system treats each channel as a separate context source:

- Website: owned positioning, product pages, pricing, claims, proof points
- Facebook: community tone, comments, reviews, long-copy posts, local trust
- YouTube: scripts, transcripts, chapters, education depth, retention hooks
- TikTok: opening hook, scene beats, captions, CTA rhythm, creator-native language
- Instagram: reels, visual identity, story highlights, lifestyle framing
- X: concise messaging, topic velocity, replies, risk and controversy signals

This prevents the system from assuming that a brand story that works on one channel will automatically work on another.

## Components

### Brand Analyzer

Turns website text, social profile text, manual brief text, and platform metadata into a structured brand profile.

### KOL Fetcher

Returns candidate creators. In demo mode it loads `data/demo_kols.json`. In live mode it can be adapted to approved APIs or data providers.

### Matcher

Runs hard eligibility gates first, then scores only eligible creators with the 7-factor model.

### Planner

Groups ranked creators into a full-funnel campaign mix such as awareness, trust building, review burst, conversion, and live commerce.

## Design Principles

- Keep platform context separate before synthesis
- Pull scripts, transcripts, captions, comments, and scene beats where authorized
- Keep ranking logic explainable
- Make data-source adapters replaceable
- Separate scoring from rationale writing
- Keep demo mode fully offline
- Keep secrets out of git
