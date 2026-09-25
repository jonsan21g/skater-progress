# Figure Skating Results Parser ⛸️

This tool automatically extracts official competition results and element scores for **Joanne Amelie SANITO** directly from Danish figure skating PDF protocol sheets (ISU Calc format).

## Location
- Script: `scripts/parse_results.py`
- Output: `data/skater-data.json`
- Source PDFs: `../results/*.pdf`

---

## What It Extracts
1. **Competition Details**:
   - Competition name, category (e.g., *FunSprings*, *Springs K1*, *Springs B2*, *Novice Girls B1*), and event date.
2. **Placement & Overall Scores**:
   - Rank / Placement (🥇 1st, 🥈 2nd, 🥉 3rd, etc.)
   - Total Segment Score
   - Technical Element Score (TES)
   - Factored Program Component Score (PCS)
   - Deductions & Variety Bonuses
3. **Element Breakdown**:
   - Every executed jump, spin, and step sequence with Base Value (BV), Grade of Execution (GOE), and Panel Score.
4. **Career Statistics & Personal Bests**:
   - Career Personal Best (Total, TES, PCS)
   - Highest scoring jump & spin
   - Total medal tally (Golds, Silvers, Bronzes)

---

## How to Run It Manually

Whenever you get a new competition PDF:
1. Place the new PDF into `c:\Users\jonsa\LLM\skater-progress\results\`
2. Open PowerShell or terminal in `c:\Users\jonsa\LLM\skater-progress\app\`
3. Run:
   ```bash
   python scripts/parse_results.py
   ```
4. The file `data/skater-data.json` will update automatically!

---

## Future Automation with GitHub Actions

When you push a new PDF to GitHub, a GitHub Actions workflow can automatically trigger this parser, commit the updated `skater-data.json`, and redeploy your web app without any manual steps.

Workflow example: `.github/workflows/update-results.yml`
```yaml
name: Update Skater Results
on:
  push:
    paths:
      - 'results/**.pdf'
jobs:
  parse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install pypdf
      - name: Run Parser
        run: |
          cd app
          python scripts/parse_results.py
      - name: Commit updated data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add app/data/skater-data.json
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto-update skater results"
          git push
```
