# 🚲 RidePulse NYC — Live Bike Intelligence

A competition-grade, live Citi Bike dashboard built with Streamlit. No uploads required — the app pulls real-time GBFS data and turns it into interactive stories, models, and maps.

## Features

- Live data (no uploads): GBFS station_information + station_status
- Snapshot history to power short-term trends and predictions
- Sidebar pages:
  - Overview — animated header, KPIs, short-term trends, highlights
  - Stations — searchable explorer, traffic labels (Low/Medium/High)
  - Trends — time-series from recent snapshots
  - Models Lab — interactive models:
    - Short-term ride prediction (moving average)
    - Busiest station classifier (KMeans)
    - Trip duration estimator (geo distance + speed)
    - Rider type predictor (heuristic)
    - Weekend vs weekday explorer
  - Fun Facts — 10+ live-generated fact cards and visuals
  - Quiz — 5-question quiz with achievement badge
  - Story Builder — auto creates interactive story beats
  - Live Map — hex heatmap + stations + arc flows (near-full → near-empty)
- Achievements: earn badges as you explore

## Quickstart

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown (typically http://localhost:8501).

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io and select your repo.
3. App file: `app.py`
4. Deploy. Done!

## Notes

- Snapshot history saves to `data/snapshots.parquet` (fallback CSV). On cloud hosts, history resets on restart.
- Map uses pydeck. Without a Mapbox token, it uses default basemaps.
- Lottie header is optional; if `streamlit-lottie` fails, the app still runs.