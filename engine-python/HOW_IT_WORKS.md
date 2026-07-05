# How It Works

The engine converts brand input into a ranked creator shortlist.

1. `brand_analyzer.py` extracts a structured brand profile.
2. `kol_fetcher.py` loads candidate creators from demo data or an external adapter.
3. `matcher.py` applies hard eligibility gates.
4. Eligible creators receive a 7-factor weighted score.
5. `planner.py` can group creators into a campaign mix.

The ranking logic is intentionally transparent so teams can tune the model for different categories and objectives.
