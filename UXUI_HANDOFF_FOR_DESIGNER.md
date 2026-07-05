# UX/UI Handoff For Designer

## Current Project State

This project is a public, reusable prototype called **TikTok KOL Matcher**. It is now designed as a **campaign planning console** rather than a simple form-and-results demo.

The browser demo is a single static file:

```text
/Users/nok/Desktop/tiktok-kol-matcher/index.html
```

Public demo URL:

```text
https://waranyutrkm.github.io/tiktok-kol-matcher/
```

The latest UI redesign is already inside `index.html`. The page now has:

- Planning-console aesthetic
- Sticky top bar
- Compact workflow hero
- Platform source cards
- Results insight chips
- Creator shortlist cards
- Campaign planning board
- Two result tabs only:
  - Quick Match
  - Campaign Planner

The previous redundant Platform Analysis tab has been removed from the UI and JavaScript.

## What The Product Does

The product helps a brand or marketing team move from campaign context to creator planning:

```text
Brand brief + platform URLs
-> platform-specific brand context
-> creator scoring
-> ranked KOL shortlist
-> platform-by-stage campaign planner
```

The core product idea is platform separation. A brand story does not behave the same way across Website, Facebook, YouTube, TikTok, Instagram, and X.

Platform interpretation:

- Website: owned proof, positioning, product claims, FAQ, review modules
- Facebook: community tone, objections, comments, long-copy trust
- YouTube: long-form education, scripts, tutorials, comparison logic
- TikTok: hooks, scene pacing, affiliate CTA, shop cues, live commerce
- Instagram: visual identity, reels, carousel proof, lifestyle framing
- X: concise message tests, replies, objections, risk signals

## Current User Flow

1. User opens the demo page.
2. User sees the console-style header and workflow summary.
3. User clicks `Run skincare demo` or scrolls to `Client input`.
4. User enters campaign setup:
   - Brand category
   - Campaign objective
   - Brand brief
5. User enters platform sources:
   - Website
   - Facebook
   - YouTube
   - TikTok
   - Instagram
   - X
6. User clicks `Find matching KOLs`.
7. Results appear with:
   - Creators scanned
   - Brand channels
   - Eligible creators
   - Top match score
   - Insight chips
   - Platform context summary
8. User can switch between:
   - Quick Match
   - Campaign Planner

## Main Files

Primary UI file:

```text
/Users/nok/Desktop/tiktok-kol-matcher/index.html
```

Designer handoff file:

```text
/Users/nok/Desktop/tiktok-kol-matcher/UXUI_HANDOFF_FOR_DESIGNER.md
```

Python engine and tests:

```text
/Users/nok/Desktop/tiktok-kol-matcher/engine-python
```

The browser demo does not call the Python engine. It is a static GitHub Pages demo with data and logic embedded in `index.html`.

## Current Page Structure

### 1. Top Bar

Current classes:

```text
topbar
topbar-in
brand
logo
wordmark
topbar-tag
topbar-right
pill
dot
```

Purpose:

- Brand the tool as `KOL Matcher / console`
- Signal that the page uses synthetic demo data
- Keep the product feeling like an operational planning tool

### 2. Hero / Workflow Intro

Current classes:

```text
hero
hero-grid
cta-row
flow
flow-title
flow-steps
fstep
idx
```

Purpose:

- Explain the workflow quickly
- Provide `Run skincare demo`
- Provide `Enter custom brief`
- Show the four-step process:
  - Brief and sources
  - Platform research
  - Creator shortlist
  - Campaign planner

### 3. KPI Strip

Current classes:

```text
kpis
kpi
num
lab
```

Current values:

- 6 brand channels
- 7 scoring factors
- 12 demo creators
- 17 engine tests

These are static in the hero and dynamic in the results section.

### 4. Client Input

Current IDs that must be preserved:

```text
form
category
objective
brief
webUrl
facebookUrl
youtubeUrl
tiktokUrl
instagramUrl
xUrl
```

Current classes:

```text
section
panel
sec-head
sec-num
sec-sub
input-grid
field
sources-head
src-grid
src-card
src-top
src-name
src-help
src-status
setup-note
run-row
```

Platform chips:

```text
pchip
pchip-website
pchip-facebook
pchip-youtube
pchip-tiktok
pchip-instagram
pchip-x
```

Important UX rule:

Platform URLs should remain visually separate. Do not collapse them into one generic URL field.

### 5. Results Overview

Current IDs:

```text
results
scanCount
platformCount
eligibleCount
topScore
insight
contextBox
```

Purpose:

- Show that processing happened
- Summarize objective, detected channels, eligible creators, and top match
- Explain platform-aware research before showing creators and planner

Current insight chips are rendered by:

```text
renderInsight(list)
```

### 6. Result Tabs

Current tabs:

```text
Quick Match
Campaign Planner
```

Current IDs:

```text
quick
planner
```

Current classes:

```text
tabs
tab
tabpane
active
hidden
```

Important:

There is no Platform Analysis tab anymore.

The old functions `industry()` and `analysisExtraction()` should not be reintroduced unless the product intentionally adds a separate research tab again.

## Quick Match Tab

Rendered by:

```text
card(c, i)
```

Current card classes:

```text
creator
creator lead
creator-head
rank
creator-id
creator-meta
score-badge
score-num
score-cap
bio
chips
chip
chip role
breakdown
metric
mlab
track
rationale
lead-tag
```

Each creator card shows:

- Rank
- TikTok profile link
- Display name
- Followers
- Engagement rate
- Match score
- Bio
- Commerce tags
- Role tags
- Seven-factor scoring breakdown
- Rationale

Scoring factors:

- Relevance
- Audience
- Objective
- Style
- Performance
- Commerce
- Safety

## Campaign Planner Tab

Rendered by:

```text
planner(list)
stageCard(platform, stageKey, list)
platformStageMatrix(platformId)
stageContentPlan(platformId, stageKey)
creatorForStage(platformId, stageKey, list)
```

Current planner classes:

```text
board-intro
platform-block
pb-head
pb-chip
pb-src
pb-role
stage-grid
stage
stage-badge
stage-awareness
stage-trust
stage-review
stage-conversion
stage-live
stage-goal
stage-meta
row
hook
stage-creator
ktag
```

Each platform block shows:

- Platform code chip
- Platform name
- Source link
- Platform role explanation
- Stage cards that are valid for that platform

Each stage card shows:

- Stage label
- Stage goal
- Content format
- Execution plan
- CTA
- Sample hook
- Suggested creator link and role

## Platform Stage Matrix

Current platform-stage matrix:

```text
Website: Awareness, Trust building, Review burst
Facebook: Awareness, Trust building, Review burst, Conversion
YouTube: Awareness, Trust building, Review burst
TikTok: Awareness, Review burst, Conversion, Live commerce
Instagram: Awareness, Trust building, Review burst, Conversion
X: Awareness, Trust building
```

Important product rule:

Do not show every stage for every platform.

Examples:

- Website should not show Live commerce.
- Website should focus on owned proof and review modules.
- TikTok can show Live commerce.
- X should stay focused on concise message tests and objection capture.

## JavaScript Functions Currently Used

Keep these functions unless there is a deliberate refactor:

```text
scrollToForm()
getPlatformContext()
runDemo()
getWeights()
updateWeightsDisplay()
toggleTheme()
updateThemeIcon()
copyConsoleLink()
loadStateFromUrl()
exportCSV()
exportJSON()
score(c)
matchCreators()
renderInsight(list)
renderContext()
render(list)
card(c, i)
analysisRole(platformId)
stageConfig()
platformStageMatrix(platformId)
creatorForStage(platformId, stageKey, list)
stageContentPlan(platformId, stageKey)
stageCard(platform, stageKey, list, stepNumber, totalSteps)
planner(list)
showMode(id, btn)
setLanguage(lang)
toggleLanguage()
getLang()
```

Removed functions:

```text
industry()
analysisExtraction()
```

## DOM IDs To Preserve

These IDs are used by JavaScript:

```text
form
category
objective
brief
webUrl
facebookUrl
youtubeUrl
tiktokUrl
instagramUrl
xUrl
results
scanCount
platformCount
eligibleCount
topScore
insight
contextBox
quick
planner
theme-btn
theme-btn-icon
theme-btn-text
w-relevance
w-audience
w-objective
w-style
w-performance
w-commerce
w-safety
lang-btn
lang-btn-text
```

Do not rename them without updating JavaScript.

## Design Notes For Future Edits

The current direction is a restrained SaaS planning console. Keep it:

- Clean
- Dense but readable
- Platform-aware
- Campaign-planning focused
- English-only
- Generic and reusable
- Clear about synthetic data and human review

Avoid:

- Turning the first screen into a generic marketing landing page
- Reintroducing redundant tabs
- Mixing all platform sources into one generic field
- Showing unavailable campaign stages for a platform
- Removing the synthetic data note
- Removing creator profile links
- Hiding the scoring rationale completely

## Static Deployment Notes

The page is deployed through GitHub Pages from:

```text
main
/
```

No build step is required.

Deployment flow:

```bash
cd /Users/nok/Desktop/tiktok-kol-matcher
git add index.html UXUI_HANDOFF_FOR_DESIGNER.md
git commit -m "Redesign demo UI + remove redundant Platform Analysis tab"
git push
```

GitHub Pages will update automatically after push.

## Test Checklist After Any Edit

1. Open the page locally.
2. Click `Run skincare demo`.
3. Confirm the Results section appears.
4. Confirm only two tabs are visible:
   - Quick Match
   - Campaign Planner
5. Confirm Quick Match renders creator cards.
6. Confirm Campaign Planner renders platform blocks.
7. Confirm Website shows only:
   - Awareness
   - Trust building
   - Review burst
8. Confirm TikTok shows:
   - Awareness
   - Review burst
   - Conversion
   - Live commerce
9. Confirm creator links open in a new tab.
10. Confirm the synthetic data note remains visible.
11. Confirm there are no JavaScript console errors.
12. Confirm Dark Mode / Light Mode toggle correctly transitions visual variables and saves to localStorage.
13. Confirm adjusting Custom Weight sliders updates creator scores and rank order dynamically in real-time.
14. Confirm Copy Link creates a shareable URL containing base64 state which successfully loads and runs the console.
15. Confirm Export Shortlist (CSV) and Export Plan (JSON) download files containing the current console data.

Command-line syntax check:

```bash
cd /Users/nok/Desktop/tiktok-kol-matcher
/Users/nok/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node -e "const fs=require('fs'); const html=fs.readFileSync('index.html','utf8'); const script=html.match(/<script>([\s\S]*)<\/script>/)[1]; new Function(script); console.log('script syntax ok');"
```

Python engine tests:

```bash
cd /Users/nok/Desktop/tiktok-kol-matcher/engine-python
python3 -B -c 'import sys, importlib; sys.path.insert(0,"."); mods=["tests.test_matcher","tests.test_pipeline","tests.test_planner"]; total=0; failed=[]
for m in mods:
    mod=importlib.import_module(m)
    for name in sorted(n for n in dir(mod) if n.startswith("test_")):
        total += 1
        try:
            getattr(mod,name)()
        except Exception as e:
            failed.append((m,name,repr(e)))
print(f"tests run: {total}, failed: {len(failed)}")
for m,n,e in failed:
    print(f"FAIL {m}.{n}: {e}")
sys.exit(1 if failed else 0)'
```

## Final Product Goal

The redesigned app should help a marketing or creator strategy team answer:

- What platforms does the brand already have?
- What does each platform contribute to research?
- Which creators fit the campaign objective?
- Why are those creators ranked?
- Which campaign stages are realistic for each platform?
- What content idea and creator role should be used per stage?

The current UI should feel like a practical creator planning console, not only a ranking demo.
