# Joanne Amelie Sanito — Figure Skating Progress & DSU Tracker ⛸️

A dedicated figure skating portfolio and progress tracking web app for **Joanne Amelie SANITO**, tracking her official competition scores, element evaluations, and competitive career progression for **Skøjteklub København (SKK)** within the **Dansk Skøjte Union (DSU)** and the **International Skating Union (ISU)**.

---

## 🌟 Profile & Career Overview
- **Skater**: Joanne Amelie SANITO
- **Club**: Skøjteklub København (SKK)
- **Federation**: Dansk Skøjte Union (DSU) / ISU
- **Current Category**: Novice Girls B1
- **Career Podiums**: 6 (🥇 4 Gold, 🥈 1 Silver, 🥉 1 Bronze) across 12 official competitions
- **Personal Best (Total Score)**: 25.13 pts (*HSK Cup 2026*)
- **PB Technical Element Score (TES)**: 14.00 pts
- **PB Program Component Score (PCS)**: 12.93 pts

---

## 🚀 Key Features

1. **Ice Glassmorphism Design**:
   - Modern dark ice aesthetic featuring dynamic ambient glow accents, frosted glass cards, and Danish national flag badge.
   - Interactive hero profile showcasing current category, club affiliation, career podium counter, and personal best markers.

2. **Interactive Career Score Progression Chart**:
   - Built with **Chart.js** tracking category progression spanning `FunSprings` ➔ `Springs K1` ➔ `Springs B2` ➔ `Novice Girls B1`.
   - Metric toggles allowing one-click switching between:
     - **Total Score**
     - **Technical Elements (TES)**
     - **Program Components (PCS)**

3. **Key Elements & Career Records**:
   - Instant spotlight on personal best executions with Base Value (BV) and Grade of Execution (GOE):
     - **Best Solo Jump**: `2T` (Double Toe Loop — 1.17 pts)
     - **Best Jump Combination**: `1Lz+1A+SEQ` (1.66 pts)
     - **Best Spin**: `CCoSp2` (Level 2 Change Foot Combination Spin — 3.00 pts, max base value)
     - **Best Step Sequence**: `StSqB` (1.70 pts)

4. **Official Competition Protocol History & Element Breakdown**:
   - Comprehensive timeline of all **12 parsed DSU competitions** (2024–2026), including HSK Cup 2026.
   - Category filtering (*All Events*, *Novice Girls B1*, *Springs B2*, *Springs K1*, *FunSprings*).
   - Expandable scorecards displaying placement badges, total segment scores, TES, PCS, deductions, and itemized panel element evaluation tables.

5. **Season Milestones & Growth Roadmap**:
   - Visual milestone tracker highlighting career promotions (FunSkate ➔ Springs ➔ Novice B1), breaking the 20-point barrier, joining the **25+ Points Club** (25.13 at HSK Cup 2026), and targeting next season goals.

6. **100% Automated Web & PDF Ingestion**:
   - Scrapes official Swiss Timing / ISU Calc results portals (`resultater.danskate.dk`) via `scripts/fetch_web_results.py`.
   - Discovers Joanne's protocol PDF automatically, downloads and archives the official document, and performs idempotent deduplication.
   - Fully automated CI/CD via GitHub Actions: runs on-push whenever `data/competitions.json` is modified, with on-demand (`workflow_dispatch`) support and auto-commit to GitHub Pages.

---

## 📂 Repository Structure

```
skater-progress/app/
├── .github/
│   └── workflows/
│       └── update-skater-data.yml # GitHub Actions workflow (on-push & on-demand)
├── data/
│   ├── competitions.json          # Target competition URLs watchlist
│   └── skater-data.json           # Compiled static database (records, scores & protocols)
├── docs/
│   └── PARSER.md                  # Results engine & scraper documentation
├── results/                       # Archived official competition PDFs (ISU Calc)
│   ├── HSK CUP 2026.pdf
│   ├── DANMARKS CUP 2025.pdf
│   ├── EFTERÅRSKONKURRENCE ØST 2026.pdf
│   └── ...
├── scripts/
│   ├── fetch_web_results.py       # Automated web portal crawler & updater
│   ├── parse_results.py           # Core ISU Calc PDF extraction engine
│   └── requirements.txt           # Python dependencies (pypdf)
├── index.html                     # Responsive single-page web app
├── style.css                      # Modern ice glassmorphism design system
├── app.js                         # Dynamic client application & Chart.js graph
└── README.md
```

---

## 💻 Local Usage & Development

### 1. Run the Web App Locally
From the `app` directory:
```bash
python -m http.server 8080
```
Then visit `http://localhost:8080` in your web browser.

### 2. Add a New Competition via URL
Simply add the competition URL into `data/competitions.json` and push to GitHub, or run locally:
```bash
python scripts/fetch_web_results.py --url https://resultater.danskate.dk/HSK26
```
This automatically downloads the official PDF, extracts all element scores, updates `data/skater-data.json`, and recalculates all-time personal bests.
