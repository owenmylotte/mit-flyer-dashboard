#!/usr/bin/env python3
"""
Fetch authoritative MIT building coordinates from whereis.mit.edu and
write them directly into the BUILDING_COORDS object in index.html.

Usage:
    python update_building_coords.py          # updates ../index.html
    python update_building_coords.py --dry-run  # print only, don't write

Source: https://whereis.mit.edu/search?type=building&output=json&q=BLDGNUM
This is MIT's official campus map API. No auth required.
"""

import argparse
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

API = "https://whereis.mit.edu/search?type=building&output=json&q={}"

# All building numbers tracked in the dashboard CSV.
BUILDINGS = [
    "1","2","3","4","5","6","6C","7","7A","8","9","10","11","12","13","14",
    "16","17","18","24","26","31","32","33","34","35","36","37","38","39",
    "41","42","43","45","46","48","50","51","54","56","57","62","64","66",
    "68","76",
    "E1","E2","E14","E15","E17","E18","E19","E23","E25","E28","E37","E38",
    "E39","E40","E48","E51","E52","E53","E55","E60","E62","E70","E90","E94",
    "N9","N10","N42","N51","N52","N57",
    "NE18","NE36","NE46","NE47","NE48","NE49","NE55","NE83","NE103",
    "NW10","NW12","NW13","NW14","NW17","NW21","NW22","NW23","NW30","NW35",
    "NW61","NW86","NW98",
    "W2","W5","W8","W11","W13","W15","W16","W18","W20","W31","W32","W35",
    "W41","W46","W59","W84","W89","W91","W92","W97","W98","WW15",
]


def fetch_building(bldg: str) -> dict | None:
    url = API.format(urllib.parse.quote(bldg))
    try:
        # Use curl — whereis.mit.edu uses a weak DH key that Python's ssl rejects
        proc = subprocess.run(
            ["curl", "-s", "--max-time", "10", url],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        results = json.loads(proc.stdout)
        # Pick the result whose bldgnum matches exactly
        for item in results:
            if item.get("bldgnum", "").upper() == bldg.upper():
                return item
        # Fallback: first result if only one returned
        if len(results) == 1:
            return results[0]
    except Exception as e:
        print(f"  ERROR fetching {bldg}: {e}")
    return None


def build_js_block(coords: dict[str, dict]) -> str:
    """Render the BUILDING_COORDS JS object literal."""
    lines = ["const BUILDING_COORDS = {"]

    sections = [
        ("Main Campus", [b for b in coords if b[0].isdigit()]),
        ("East Campus", [b for b in coords if b.startswith("E")]),
        ("North Campus", [b for b in coords if b.startswith("N") and not b.startswith("NE") and not b.startswith("NW")]),
        ("Northeast Campus", [b for b in coords if b.startswith("NE")]),
        ("Northwest Campus", [b for b in coords if b.startswith("NW")]),
        ("West Campus", [b for b in coords if b.startswith("W") or b.startswith("WW")]),
    ]

    def sort_key(b):
        prefix = re.sub(r'\d.*', '', b)
        num = re.sub(r'\D', '', b)
        return (prefix, int(num) if num else 0)

    for section_name, keys in sections:
        if not keys:
            continue
        lines.append(f"\n  // {section_name} Buildings")
        for b in sorted(keys, key=sort_key):
            d = coords[b]
            lines.append(f'  "{b}": {{ lat: {d["lat"]}, lng: {d["lng"]}, name: "{d["name"]}" }},')

    lines.append("};")
    return "\n".join(lines)


def patch_index_html(html_path: Path, js_block: str) -> str:
    content = html_path.read_text()
    # Replace everything between (and including) the const BUILDING_COORDS = {
    # line and the closing };
    pattern = r'const BUILDING_COORDS = \{.*?\};'
    new_content = re.sub(pattern, js_block, content, flags=re.DOTALL)
    if new_content == content:
        raise ValueError("Could not find BUILDING_COORDS in index.html — pattern not matched")
    return new_content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print JS block without writing")
    args = parser.parse_args()

    html_path = Path(__file__).parent.parent / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    coords: dict[str, dict] = {}
    failed = []
    total = len(BUILDINGS)

    print(f"Fetching {total} buildings from whereis.mit.edu...\n")
    for i, bldg in enumerate(BUILDINGS, 1):
        print(f"  [{i:>3}/{total}] {bldg:<8}", end=" ", flush=True)
        result = fetch_building(bldg)
        if result:
            lat = round(result["lat_wgs84"], 6)
            lng = round(result["long_wgs84"], 6)
            name = result.get("name") or f"Building {bldg}"
            coords[bldg] = {"lat": lat, "lng": lng, "name": name}
            print(f"→ {lat}, {lng}  ({name})")
        else:
            failed.append(bldg)
            print("→ NOT FOUND")
        time.sleep(0.15)  # be polite to the API

    print(f"\nFetched {len(coords)} / {total}. Failed: {failed or 'none'}")

    js_block = build_js_block(coords)

    if args.dry_run:
        print("\n--- JS block ---")
        print(js_block)
        return

    new_html = patch_index_html(html_path, js_block)
    html_path.write_text(new_html)
    print(f"\nUpdated {html_path}")

    if failed:
        print(f"\nWARNING: These buildings had no whereis.mit.edu entry and kept old coords:")
        for b in failed:
            print(f"  {b}")


if __name__ == "__main__":
    main()
