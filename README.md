# Joanne Amelie Sanito — Figure Skating Progress & DSU Tracker ⛸️

A dedicated figure skating portfolio and progress tracking web app for **Joanne Amelie SANITO**, tracking her official competition scores, element evaluations, and competitive career progression for **Skøjteklub København (SKK)** within the **Dansk Skøjte Union (DSU)** and the **International Skating Union (ISU)**.

---

## 🌟 Profile & Career Overview
- **Skater**: Joanne Amelie SANITO
- **Club**: Skøjteklub København (SKK)
- **Federation**: Dansk Skøjte Union (DSU) / ISU
- **Current Category**: Novice Girls B1
- **Career Podiums**: 6 (🥇 4 Gold, 🥈 1 Silver, 🥉 1 Bronze) across 11 official competitions
- **Personal Best (Total Score)**: 24.58 pts (*Efterårskonkurrence Øst 2026*)
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
   - Comprehensive timeline of all **11 parsed DSU competitions** (2024–2026).
   - Category filtering (*All Events*, *Novice Girls B1*, *Springs B2*, *Springs K1*, *FunSprings*).
   - Expandable scorecards displaying placement badges, total segment scores, TES, PCS, deductions, and itemized panel element evaluation tables.

5. **Season Milestones & Growth Roadmap**:
   - Visual milestone tracker highlighting career promotions (FunSkate ➔ Springs ➔ Novice B1), breaking the 20-point barrier, executing Level 2 spins, and targeting the 25+ point threshold.

6. **Automated PDF Protocol Parser**:
   - Python-based parser (`scripts/parse_results.py`) utilizing `pypdf`.
   - Ingests official Danish figure skating PDF protocol sheets (ISU Calc standard), extracts skater placements, TES, PCS, and individual element scores, and compiles clean static JSON directly into `data/skater-data.json`.
   - Designed for zero-maintenance CI/CD workflow automation via GitHub Actions.

---

## 📂 Repository Structure

```
skater-progress/
├── results/                       # Source competition PDF protocols (ISU Calc format)
│   ├── DANMARKS CUP 2025.pdf
│   ├── EFTERÅRSKONKURRENCE ØST 2026.pdf
│   ├── FLYVER CUP 2026.pdf
│   └── ...
└── app/                           # Web application & scraper engine (Git Root)
    ├── data/
    │   └── skater-data.json       # Compiled database (records, scores & protocols)
    ├── docs/
    │   └── PARSER.md              # PDF scraper documentation & CI/CD workflow
    ├── scripts/
    │   └── parse_results.py       # ISU Calc PDF protocol extraction script
    ├── index.html                 # Responsive single-page web app
    ├── style.css                  # Modern ice glassmorphism design system
    ├── app.js                     # Dynamic client application & Chart.js graph
    └── README.md
```

---

## 💻 Local Development

### 1. Run the Web App Locally
From the `app` directory:
```bash
python -m http.server 8080
```
Then visit `http://localhost:8080` in your web browser.

### 2. Update Competition Data
When a new competition protocol PDF is available:
1. Place the PDF in `../results/`
2. Run the parser script:
```bash
# Install dependency (if needed)
pip install pypdf

# Run parser from app directory
python scripts/parse_results.py
```
3. `data/skater-data.json` will update automatically with newly computed personal bests, medal tallies, and score breakdowns.
