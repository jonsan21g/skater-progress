"""
Automated Danish Figure Skating Web Scraper & Results Updater
Fetches official competition protocols directly from resultater.danskate.dk
and updates skater-data.json with full deduplication and record recalculation.
"""

import os
import sys
import re
import json
import io
import argparse
import urllib.request
import pypdf
from datetime import datetime

# Configure UTF-8 encoding for standard output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Import parsing helpers from parse_results
from parse_results import (
    clean_danish_text,
    standardize_category,
    standardize_competition_name,
    parse_page_for_skater,
    SKATER_NAME_KEYWORD,
    OUTPUT_DATA_PATH,
    RESULTS_DIR
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPETITIONS_JSON = os.path.join(BASE_DIR, "data", "competitions.json")
PARENT_RESULTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "results"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_url_content(url):
    """Fetches binary content from URL with User-Agent header."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def normalize_comp_key(name):
    """Normalizes competition name for fuzzy deduplication."""
    cleaned = clean_danish_text(name).lower()
    cleaned = re.sub(r'[^a-z0-9]', '', cleaned)
    return cleaned

def fetch_competition_from_url(url, comp_name_hint=None):
    """
    Connects to an ISU Calc / Swiss Timing result portal on resultater.danskate.dk,
    discovers Judges Scores PDFs, searches for Joanne SANITO, and returns parsed data and PDF bytes.
    """
    clean_url = url.rstrip('/')
    index_url = clean_url if clean_url.endswith('.htm') or clean_url.endswith('.html') else f"{clean_url}/index.htm"
    base_url = index_url.rsplit('/', 1)[0]

    print(f"\n🌐 Scanning portal: {index_url}")
    try:
        html_bytes = fetch_url_content(index_url)
        html_text = html_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Failed to reach {index_url}: {e}")
        return None

    # Detect title
    title_match = re.search(r'<title>([^<]+)</title>', html_text, re.IGNORECASE)
    portal_title = title_match.group(1).strip() if title_match else (comp_name_hint or "Competition")
    print(f"   Competition Title: {portal_title}")

    # Extract all PDF links
    pdf_links = re.findall(r'href=[\x22\x27]?([^\x22\x27\s>]+\.pdf)', html_text, re.IGNORECASE)
    # Deduplicate preserving order
    pdf_links = list(dict.fromkeys(pdf_links))
    print(f"   Found {len(pdf_links)} PDF protocol links on portal.")

    for pdf_rel in pdf_links:
        full_pdf_url = pdf_rel if pdf_rel.startswith('http') else f"{base_url}/{pdf_rel}"
        try:
            pdf_bytes = fetch_url_content(full_pdf_url)
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            for page_idx, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt and SKATER_NAME_KEYWORD in txt.upper():
                    print(f"   🎯 Found {SKATER_NAME_KEYWORD} in {pdf_rel} (Page {page_idx + 1})")
                    filename_for_parser = f"{portal_title}.pdf"
                    parsed = parse_page_for_skater(txt, filename_for_parser)
                    if parsed:
                        parsed["sourceUrl"] = url
                        parsed["sourcePdfUrl"] = full_pdf_url
                        return {
                            "parsed": parsed,
                            "pdf_bytes": pdf_bytes,
                            "suggested_filename": f"{portal_title.upper()}.pdf"
                        }
        except Exception as err:
            # Continue scanning other PDFs
            continue

    print(f"   ⚠️ Skater {SKATER_NAME_KEYWORD} not found in any protocol PDFs for {url}")
    return None

def recalculate_career_records(competitions):
    """Recalculates Personal Bests, top elements, and medal tallies across all competitions."""
    competitions.sort(key=lambda x: x["date"])

    pb_total = max([c["totalScore"] for c in competitions], default=0.0)
    pb_tes = max([c["tes"] for c in competitions], default=0.0)
    pb_pcs = max([c["pcs"] for c in competitions], default=0.0)

    solo_jumps = []
    combos = []
    spins = []
    step_sequences = []

    for c in competitions:
        for el in c.get("elements", []):
            el_with_comp = dict(el)
            el_with_comp["competition"] = c["competition"]
            el_with_comp["date"] = c["date"]
            
            code = el["code"]
            if el["type"] == "jump":
                if "+" in code or "SEQ" in code:
                    combos.append(el_with_comp)
                else:
                    solo_jumps.append(el_with_comp)
            elif el["type"] == "spin":
                spins.append(el_with_comp)
            elif el["type"] == "step" or "StSq" in code or "ChSq" in code:
                step_sequences.append(el_with_comp)

    best_solo_jump = max(solo_jumps, key=lambda x: x["score"]) if solo_jumps else None
    best_combo = max(combos, key=lambda x: x["score"]) if combos else None
    best_spin = max(spins, key=lambda x: x["score"]) if spins else None
    best_step_seq = max(step_sequences, key=lambda x: x["score"]) if step_sequences else None

    gold_medals = sum(1 for c in competitions if c.get("rank") == 1)
    silver_medals = sum(1 for c in competitions if c.get("rank") == 2)
    bronze_medals = sum(1 for c in competitions if c.get("rank") == 3)

    return {
        "personalBestTotal": pb_total,
        "personalBestTES": pb_tes,
        "personalBestPCS": pb_pcs,
        "bestSoloJump": best_solo_jump,
        "bestCombo": best_combo,
        "bestSpin": best_spin,
        "bestStepSeq": best_step_seq,
        "medals": {
            "gold": gold_medals,
            "silver": silver_medals,
            "bronze": bronze_medals,
            "total": gold_medals + silver_medals + bronze_medals
        },
        "totalEvents": len(competitions)
    }

def update_database_with_results(new_results):
    """
    Safely merges new competition records into skater-data.json with strict deduplication.
    Guarantees backward compatibility by preserving existing records.
    """
    if os.path.exists(OUTPUT_DATA_PATH):
        with open(OUTPUT_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "skater": {
                "name": "Joanne Amelie SANITO",
                "club": "Skøjteklub København (SKK)",
                "currentCategory": "Novice Girls B1",
                "federation": "Dansk Skøjte Union (DSU) / ISU"
            },
            "records": {},
            "competitions": []
        }

    competitions = data.get("competitions", [])
    updated_count = 0
    added_count = 0

    for result in new_results:
        parsed = result["parsed"]
        pdf_bytes = result.get("pdf_bytes")
        suggested_filename = result.get("suggested_filename")

        # Save PDF to local results folder for backup
        if pdf_bytes and suggested_filename:
            pdf_path = os.path.join(RESULTS_DIR, suggested_filename)
            try:
                with open(pdf_path, "wb") as pf:
                    pf.write(pdf_bytes)
                print(f"   💾 Saved protocol PDF to {pdf_path}")
            except Exception as e:
                print(f"   ⚠️ Could not save PDF to {pdf_path}: {e}")

            if os.path.exists(PARENT_RESULTS_DIR):
                parent_pdf_path = os.path.join(PARENT_RESULTS_DIR, suggested_filename)
                try:
                    with open(parent_pdf_path, "wb") as pf:
                        pf.write(pdf_bytes)
                except Exception:
                    pass

        # Deduplication check
        target_name_key = normalize_comp_key(parsed["competition"])
        target_date = parsed.get("date", "")
        target_url = parsed.get("sourceUrl", "")

        match_idx = -1
        for idx, existing in enumerate(competitions):
            existing_name_key = normalize_comp_key(existing["competition"])
            existing_date = existing.get("date", "")
            existing_url = existing.get("sourceUrl", "")

            # Match by URL if present, or by normalized name + year
            if target_url and existing_url and target_url.rstrip('/').lower() == existing_url.rstrip('/').lower():
                match_idx = idx
                break
            if target_name_key == existing_name_key:
                if not target_date or not existing_date or target_date[:4] == existing_date[:4]:
                    match_idx = idx
                    break

        if match_idx >= 0:
            print(f"   🔄 Updating existing competition entry: {competitions[match_idx]['competition']}")
            competitions[match_idx] = parsed
            updated_count += 1
        else:
            print(f"   ✨ Adding new competition: {parsed['competition']} ({parsed['date']})")
            competitions.append(parsed)
            added_count += 1

    # Recalculate records across all events
    data["competitions"] = competitions
    data["records"] = recalculate_career_records(competitions)
    if competitions:
        data["skater"]["currentCategory"] = competitions[-1]["category"]

    with open(OUTPUT_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Database successfully updated: {OUTPUT_DATA_PATH}")
    print(f"   Total competitions: {len(competitions)} (Added: {added_count}, Updated: {updated_count})")
    print(f"   New PB: {data['records']['personalBestTotal']} pts | Career Podiums: {data['records']['medals']['total']}")

def main():
    parser = argparse.ArgumentParser(description="Fetch figure skating results from resultater.danskate.dk")
    parser.add_argument("--url", help="Direct URL of the competition portal (e.g. https://resultater.danskate.dk/HSK26)")
    parser.add_argument("--all", action="store_true", help="Process all entries in data/competitions.json")
    args = parser.parse_args()

    targets = []
    if args.url:
        targets.append({"name": "CLI Target", "url": args.url})
    elif os.path.exists(COMPETITIONS_JSON):
        with open(COMPETITIONS_JSON, "r", encoding="utf-8") as f:
            targets = json.load(f)
    else:
        print(f"No targets found in {COMPETITIONS_JSON} and no --url provided.")
        return

    print(f"⛸️ Processing {len(targets)} competition target(s)...")
    results_to_save = []
    for item in targets:
        url = item.get("url")
        name = item.get("name")
        res = fetch_competition_from_url(url, comp_name_hint=name)
        if res:
            results_to_save.append(res)

    if results_to_save:
        update_database_with_results(results_to_save)
    else:
        print("No new results extracted.")

if __name__ == "__main__":
    main()
