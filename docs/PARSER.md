# Figure Skating Results Ingestion Engine ⛸️

This tool automates the extraction and tracking of official competition results and element scores for **Joanne Amelie SANITO** from both online portals (`resultater.danskate.dk`) and Danish figure skating PDF protocol sheets (ISU Calc format).

---

## 📁 Key Files & Architecture
- **Watchlist Config**: `data/competitions.json` (List of target competition URLs)
- **Web Fetcher & Updater**: `scripts/fetch_web_results.py` (Scans portals, finds Joanne's category, downloads PDFs, and updates records)
- **Direct PDF Parser**: `scripts/parse_results.py` (Parses local protocol PDFs in `results/`)
- **Output Database**: `data/skater-data.json` (Consumed by web app)
- **GitHub Actions Workflow**: `.github/workflows/update-skater-data.yml`

---

## 🚀 How It Works

### Option A: Fully Automated (GitHub Actions)
1. Add the competition link to `data/competitions.json`:
   ```json
   [
     {
       "name": "HSK Cup 2026",
       "url": "https://resultater.danskate.dk/HSK26"
     }
   ]
   ```
2. Commit and push:
   ```bash
   git add data/competitions.json
   git commit -m "chore: add HSK Cup 2026"
   git push origin main
   ```
3. GitHub Actions triggers automatically on-push:
   - Connects to the results portal.
   - Locates Joanne's category protocol PDF.
   - Downloads and archives the PDF to `results/`.
   - Idempotently merges the results into `data/skater-data.json`.
   - Recalculates all-time personal bests (Total, TES, PCS) and medal tallies.
   - Auto-commits and publishes to GitHub Pages!

You can also trigger an immediate update anytime without pushing code by clicking **"Run workflow"** in the GitHub Actions tab (`workflow_dispatch`).

---

### Option B: Local CLI Execution

#### 1. Fetch from Watchlist
```bash
python scripts/fetch_web_results.py --all
```

#### 2. Fetch from a Specific URL On-Demand
```bash
python scripts/fetch_web_results.py --url https://resultater.danskate.dk/HSK26
```

#### 3. Parse Local Offline PDFs
If you have an offline PDF file directly:
1. Place it in `results/`
2. Run:
   ```bash
   python scripts/parse_results.py
   ```
