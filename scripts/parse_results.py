import os
import glob
import re
import json
from datetime import datetime
import pypdf

SKATER_NAME_KEYWORD = "SANITO"
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
OUTPUT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "skater-data.json"))

def clean_danish_text(s):
    if not isinstance(s, str):
        return s
    # Strip byte artifacts
    s = "".join([c for c in s if ord(c) != 216 and ord(c) != 65533])
    s = s.replace("?ST", "ØST").replace("?st", "øst")
    s = s.replace("EFTERRSKONKURRENCE", "EFTERÅRSKONKURRENCE")
    s = s.replace("EFTERRSKONKURRENCEN", "EFTERÅRSKONKURRENCEN")
    s = s.replace("FORRSKONKURRENCEN", "FORÅRSKONKURRENCEN")
    s = s.replace("SJLLANDSMESTERSKABERNE", "SJÆLLANDSMESTERSKABERNE")
    s = s.replace("SJLLANDS", "SJÆLLANDS")
    s = s.replace("ISBLOM?STEN", "ISBLOMSTEN").replace("ISBLOMSTEN", "ISBLOMSTEN")
    s = s.replace("BASIC-LBERE", "BASIC-LØBERE")
    s = s.replace("Sk?jteklub K?benhavn", "Skøjteklub København")
    s = s.replace("Dansk Sk?jte Union", "Dansk Skøjte Union")
    
    # Remove artificial spacing between single capital letters (e.g. S P R I N G S)
    s = re.sub(r'(?<=[A-Za-z0-9])\s+(?=[A-Za-z0-9]\b)', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def standardize_category(raw_cat):
    clean = clean_danish_text(raw_cat).upper()
    if "NOVICE" in clean:
        return "Novice Girls B1"
    elif "SPRINGS B2" in clean:
        return "Springs B2"
    elif "SPRINGS K1" in clean:
        return "Springs K1"
    elif "FUNSPRINGS" in clean:
        return "FunSprings"
    elif "SPRINGS" in clean:
        return "Springs"
    return clean_danish_text(raw_cat).title()

def standardize_competition_name(name):
    u = name.upper()
    if "DANMARKS CUP" in u:
        return "Danmarks Cup 2025"
    if "EFTER" in u and "2026" in u:
        return "Efterårskonkurrence Øst 2026"
    if "EFTER" in u and "2025" in u:
        return "Efterårskonkurrencen Øst 2025"
    if "ESK CUP" in u:
        return "ESK Cup 2024"
    if "FLYVER CUP" in u and "2025" in u:
        return "Flyver Cup 2025"
    if "FLYVER CUP" in u and "2026" in u:
        return "Flyver Cup 2026"
    if "FOR" in u and "2026" in u:
        return "Forårskonkurrencen Øst 2026"
    if "ISBLOMSTEN" in u:
        return "Isblomsten 2026"
    if "OKTOBER" in u:
        return "Oktoberkonkurrencen 2025"
    if "PINGVIN" in u:
        return "Pingvin Cup 2026"
    if "SJ" in u and "2024" in u:
        return "Sjællandsmesterskaberne & Sjællands Cup 2024"
    return clean_danish_text(name).title()

def parse_page_for_skater(text, filename):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if SKATER_NAME_KEYWORD not in text.upper():
        return None

    comp_name = filename.replace(".pdf", "")
    category = "Free Skating"
    date_str = ""

    for l in lines[:15]:
        if any(w in l.upper() for w in ["FREE SKATING", "SHORT PROGRAM", "ELEMENTS"]):
            category = l
        if "printed:" in l.lower():
            m_date = re.search(r"printed:\s*(\d{2}\.\d{2}\.\d{4})", l)
            if m_date:
                date_str = m_date.group(1)

    if not date_str:
        m_yr = re.search(r"202\d", filename + " " + comp_name)
        if m_yr:
            date_str = f"01.01.{m_yr.group(0)}"

    name_line_idx = -1
    for idx, l in enumerate(lines):
        if SKATER_NAME_KEYWORD in l.upper():
            name_line_idx = idx
            break

    if name_line_idx == -1:
        return None

    rank = None
    total_score = 0.0
    tes = 0.0
    pcs = 0.0
    deductions = 0.0

    # Look backwards for rank
    for b in range(1, 4):
        prev_idx = name_line_idx - b
        if prev_idx >= 0 and lines[prev_idx].isdigit():
            rank = int(lines[prev_idx])
            break

    curr_tokens = lines[name_line_idx].split()
    if rank is None and curr_tokens and curr_tokens[0].isdigit():
        rank = int(curr_tokens[0])

    chunk_to_search = " ".join(lines[max(0, name_line_idx-1):min(len(lines), name_line_idx+12)])
    score_matches = re.findall(r"\b\d+\.\d{2}\b", chunk_to_search)
    if len(score_matches) >= 4:
        total_score = float(score_matches[0])
        tes = float(score_matches[1])
        pcs = float(score_matches[2])
        deductions = float(score_matches[3])

    elements = []
    variety_bonus = 0.0
    
    exec_idx = -1
    for idx in range(name_line_idx, min(len(lines), name_line_idx + 25)):
        if "Executed Elements" in lines[idx] or "Scores of" in lines[idx]:
            exec_idx = idx
            break
            
    start_el = exec_idx + 1 if exec_idx != -1 else name_line_idx + 1
    
    for idx in range(start_el, len(lines)):
        l = lines[idx]
        if "Program Components" in l or "Rank" in l:
            break
        if "Variety Bonus" in l:
            vb_m = re.findall(r"\d+\.\d{2}", l)
            if vb_m:
                variety_bonus = float(vb_m[0])
            continue

        # Single line element row
        m1 = re.match(r"^(\d+)\s+([A-Za-z0-9\+\<\>\!\*e\-\_]+)\s+.*?(\d+\.\d{2})\s+([\-\+]?\d+\.\d{2}).*?(\d+\.\d{2})$", l)
        if m1:
            num = int(m1.group(1))
            code = clean_danish_text(m1.group(2))
            base_val = float(m1.group(3))
            goe = float(m1.group(4))
            score = float(m1.group(5))
            if score == 0.0 and base_val > 0:
                score = round(base_val + goe, 2)
            
            el_type = "other"
            if any(j in code for j in ["1", "2", "3", "A", "T", "S", "Lo", "F", "Lz", "Eu"]) and "Sp" not in code and "StSq" not in code and "Gl" not in code:
                el_type = "jump"
            elif "Sp" in code:
                el_type = "spin"
            elif any(s in code for s in ["StSq", "ChSq", "Gl"]):
                el_type = "step"

            elements.append({
                "number": num,
                "code": code,
                "type": el_type,
                "baseValue": base_val,
                "goe": goe,
                "score": score
            })
        elif l.isdigit() and idx + 1 < len(lines):
            next_l = lines[idx+1]
            if re.match(r"^[A-Za-z0-9\+\<\>\!\*e\-\_]+$", next_l):
                sub_chunk = " ".join(lines[idx:idx+12])
                sub_floats = re.findall(r"[\-\+]?\d+\.\d{2}", sub_chunk)
                if len(sub_floats) >= 3:
                    num = int(l)
                    code = clean_danish_text(next_l)
                    base_val = float(sub_floats[0])
                    goe = float(sub_floats[1])
                    score = float(sub_floats[-1])
                    if score == 0.0 and base_val > 0:
                        score = round(base_val + goe, 2)
                    
                    el_type = "other"
                    if any(j in code for j in ["1", "2", "3", "A", "T", "S", "Lo", "F", "Lz", "Eu"]) and "Sp" not in code and "StSq" not in code and "Gl" not in code:
                        el_type = "jump"
                    elif "Sp" in code:
                        el_type = "spin"
                    elif any(s in code for s in ["StSq", "ChSq", "Gl"]):
                        el_type = "step"

                    # Ensure score is panel score not total TES sum
                    if score <= 0 or score > (base_val * 2.5 + 1.0):
                        score = round(max(0.0, base_val + goe), 2)

                    if not any(e["number"] == num for e in elements):
                        elements.append({
                            "number": num,
                            "code": code,
                            "type": el_type,
                            "baseValue": base_val,
                            "goe": goe,
                            "score": score
                        })

    # Extract detailed Program Component Scores (PCS)
    pcs_details = {
        "components": [],
        "factoredTotal": pcs,
        "deductions": deductions,
        "deductionsDetail": "0.00"
    }

    pcs_components_names = ['Composition', 'Presentation', 'Skating Skills']
    pcs_start_idx = -1
    for idx in range(name_line_idx, len(lines)):
        if "Program Components" in lines[idx]:
            pcs_start_idx = idx
            break

    if pcs_start_idx != -1:
        p_idx = pcs_start_idx
        while p_idx < len(lines):
            line = lines[p_idx]
            if "Rank Name" in line or ("Page " in line and p_idx > pcs_start_idx + 10):
                break
            
            for pcs_comp in pcs_components_names:
                if line.startswith(pcs_comp):
                    floats = re.findall(r'\b\d+\.\d{2}\b', line)
                    if len(floats) >= 2:
                        pcs_details["components"].append({
                            "component": pcs_comp,
                            "factor": float(floats[0]),
                            "judges": [float(x) for x in floats[1:-1]],
                            "score": float(floats[-1])
                        })
                    else:
                        floats = []
                        k = p_idx + 1
                        while k < len(lines) and not any(lines[k].startswith(pc) for pc in pcs_components_names) and not any(w in lines[k] for w in ['Judges Total', 'Deductions', 'Rank', 'Page ']):
                            fl = re.findall(r'\b\d+\.\d{2}\b', lines[k])
                            floats.extend(fl)
                            k += 1
                        if len(floats) >= 2:
                            pcs_details["components"].append({
                                "component": pcs_comp,
                                "factor": float(floats[0]),
                                "judges": [float(x) for x in floats[1:-1]],
                                "score": float(floats[-1])
                            })
                    break

            if "Deductions:" in line:
                m_ded = re.search(r"Deductions:\s*([^\n]+)", line)
                if m_ded:
                    pcs_details["deductionsDetail"] = m_ded.group(1).strip()
            
            p_idx += 1

    iso_date = ""
    if date_str:
        try:
            d_obj = datetime.strptime(date_str, "%d.%m.%Y")
            iso_date = d_obj.strftime("%Y-%m-%d")
        except Exception:
            iso_date = date_str

    comp_name_clean = standardize_competition_name(comp_name)
    std_category = standardize_category(category)

    return {
        "sourceFile": filename,
        "competition": comp_name_clean,
        "category": std_category,
        "rawCategory": clean_danish_text(category),
        "date": iso_date or date_str,
        "rank": rank,
        "totalScore": total_score,
        "tes": tes,
        "pcs": pcs,
        "deductions": deductions,
        "varietyBonus": variety_bonus,
        "elements": elements,
        "pcsDetails": pcs_details
    }

def run():
    print(f"Scanning directory: {RESULTS_DIR}")
    pdf_files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.pdf")))
    print(f"Found {len(pdf_files)} PDF files.")

    all_competitions = []
    for pdf in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf)
            for page in reader.pages:
                txt = page.extract_text()
                if txt and SKATER_NAME_KEYWORD in txt.upper():
                    res = parse_page_for_skater(txt, os.path.basename(pdf))
                    if res:
                        print(f"[{res['date']}] {res['competition']} | Category: {res['category']} -> Rank {res['rank']}, Score: {res['totalScore']}")
                        all_competitions.append(res)
                        break
        except Exception as e:
            print(f"Error parsing {pdf}: {e}")

    # Chronological sort
    all_competitions.sort(key=lambda x: x["date"])

    # Personal Bests & Records
    pb_total = max([c["totalScore"] for c in all_competitions], default=0.0)
    pb_tes = max([c["tes"] for c in all_competitions], default=0.0)
    pb_pcs = max([c["pcs"] for c in all_competitions], default=0.0)

    solo_jumps = []
    combos = []
    spins = []
    step_sequences = []

    for c in all_competitions:
        for el in c["elements"]:
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

    gold_medals = sum(1 for c in all_competitions if c["rank"] == 1)
    silver_medals = sum(1 for c in all_competitions if c["rank"] == 2)
    bronze_medals = sum(1 for c in all_competitions if c["rank"] == 3)

    output = {
        "skater": {
            "name": "Joanne Amelie SANITO",
            "club": "Skøjteklub København (SKK)",
            "currentCategory": all_competitions[-1]["category"] if all_competitions else "Novice Girls B1",
            "federation": "Dansk Skøjte Union (DSU) / ISU"
        },
        "records": {
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
            "totalEvents": len(all_competitions)
        },
        "competitions": all_competitions
    }

    with open(OUTPUT_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully generated {OUTPUT_DATA_PATH}")
    print(f"Total events: {len(all_competitions)}")
    print(f"Categories present: {sorted(list(set(c['category'] for c in all_competitions)))}")

if __name__ == "__main__":
    run()
