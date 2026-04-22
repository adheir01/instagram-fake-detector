# Instagram Fake Follower Detector

A production-style data system for evaluating influencer audience authenticity using behavioral signals and statistical heuristics, designed to support marketing spend decisions.

**Built by [Tobi](https://www.linkedin.com/in/tobi-a-k-01/)**,  Senior Data Analyst as a part of my data portfolio. :)

---

![App screenshot](docs/screenshot.png)

---

## The problem

Influencer marketing fraud costs brands an estimated $1.3 billion annually. Small brands have no affordable way to verify whether an influencer's audience is genuinely engaged or padded with purchased followers. Commercial tools like HypeAuditor exist but are priced for enterprise. This tool makes the core analysis accessible to anyone.

---

## What it does

Input any public Instagram username and get:

- A **Fake Score (0–100)** with risk level — low / medium / high
- A **signal breakdown** explaining which patterns drove the score
- An optional **AI-generated sponsor recommendation** via Gemini API
- A downloadable **PDF report** for sharing with stakeholders

---

## How the scoring works

| Signal | What it measures | Red flag |
|---|---|---|
| Engagement rate | (likes + comments) / followers — tiered by account size | Below 0.5% for small accounts |
| Follower/following ratio | Followers vs accounts followed back | Close to 1:1 |
| Ghost follower estimate | Expected vs actual engagement gap | Above 60% |
| Posting consistency | Coefficient of variation of gaps between posts | CV below 0.2 (robotic schedule) |
| Bio completeness | Name, bio text, external URL present | Below 30% complete |

**Note on tiered baselines:** Engagement rate naturally decays at scale. A 274M follower account will never hit 3% engagement — that's normal, not suspicious. The model applies size-adjusted thresholds rather than a flat baseline.

---

## Known limitations

- **Ghost follower estimate is a heuristic** — not a direct measurement. Real detection requires follower-level scraping.
- **Engagement decay varies by niche** — a meme account and a B2B thought leader behave differently at the same follower count.
- **Private accounts lose engagement data** — scoring falls back to profile-level signals only with lower confidence.
- **Classifier needs labeled data** — current scoring is rule-based. XGBoost model is scaffolded and ready to train with 200+ labeled profiles.

---

## Tech stack

| Layer | Tools |
|---|---|
| Data collection | Python, Apify (`apify/instagram-profile-scraper` + `instagram-scraper/fast-instagram-post-scraper`) |
| Feature engineering | Pandas, NumPy |
| ML model | XGBoost, scikit-learn |
| Database | PostgreSQL |
| App | Streamlit |
| AI narrative | Gemini API (optional) |
| PDF export | ReportLab |
| Infrastructure | Docker, Docker Compose |

---

## Architecture

Two Apify actors run in sequence and are joined on `username`:

```
Actor 1: instagram-profile-scraper   →  followers, following, bio, verified
Actor 2: fast-instagram-post-scraper →  likes, comments, timestamps per post

Join on username
    ↓
Feature engineering (5 signals)
    ↓
Rule-based scorer (XGBoost when model is trained)
    ↓
Signal interpretation + risk level
    ↓
Optional: Gemini API generates sponsor recommendation
    ↓
Streamlit UI + PDF export
```

---

## Getting started

**Prerequisites:** Docker Desktop · Apify account (free tier) · Gemini API key (optional)

```bash
git clone https://github.com/adheir01/instagram-fake-detector.git
cd instagram-fake-detector
cp .env.example .env
# Add APIFY_API_TOKEN to .env
# Add GEMINI_API_KEY to .env for AI summaries
docker-compose up --build
# App runs at http://localhost:8502
```

**Test without API credits:** Click **Try Demo Data** — loads from `data/fixtures/` with no API calls.

**Train the classifier:**
```bash
docker-compose exec app python -m src.model.train
```
See `data/labeled/README.md` for labeling guide.

---

## Prior work

- **SybilRank** (Cao et al., 2012) — graph-based fake account detection using network structure
- **"The Rise of Social Bots"** (Ferrara et al., 2016) — comprehensive survey, freely available
- **HypeAuditor** — commercial state-of-the-art using follower-level scraping at scale

Academic term: **inauthentic behaviour detection**

---

## Roadmap

- [ ] Follower-level scraping for direct ghost detection
- [ ] Niche-specific engagement benchmarks
- [ ] Private account confidence scoring
- [ ] dbt metrics layer (Project 02)
- [ ] Multi-account ROI comparison (Project 02)
- [ ] Engagement anomaly detection on time series (Project 03)

---

## Disclaimer

This project is for educational purposes only. All data is collected via official Apify actors interacting with publicly available Instagram data. Users are responsible for ensuring compliance with Instagram's Terms of Service and applicable data protection laws.
