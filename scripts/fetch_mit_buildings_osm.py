#!/usr/bin/env python3
"""
Fetch MIT building coordinates from OpenStreetMap via Overpass API.

Queries all buildings in the MIT campus bounding box tagged with
operator=Massachusetts Institute of Technology, then matches them
to the building numbers used in the dashboard.

Usage:
    pip install requests
    python fetch_mit_buildings_osm.py

Output:
    buildings_osm.js  — drop-in replacement for the BUILDING_COORDS object
    buildings_osm_unmatched.txt  — OSM buildings that couldn't be matched
"""

import json
import re
import time
import requests

# MIT campus bounding box (south, west, north, east)
BBOX = "42.348, -71.107, 42.370, -71.075"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Query: all ways/relations tagged as MIT buildings, get centroid
QUERY = f"""
[out:json][timeout:60];
(
  way["operator"="Massachusetts Institute of Technology"]({BBOX});
  way["operator:wikidata"="Q49108"]({BBOX});
  way["name"~"MIT|Massachusetts Institute of Technology",i]["building"]({BBOX});
  relation["operator"="Massachusetts Institute of Technology"]({BBOX});
);
out center tags;
"""

# Known building number patterns MIT uses in OSM ref/name tags.
# OSM usually stores the number in one of these fields.
REF_FIELDS = ["ref", "name", "addr:housenumber", "short_name", "loc_name"]

# Regex to extract a building number like "32", "E14", "NW35", etc.
BLDG_NUM_RE = re.compile(
    r"\b([A-Z]{0,3}[0-9]+[A-Z]?)\b"
)

# Buildings in the dashboard that we want to find coords for
# (just the keys — pulled from the existing buildings_data.js list)
WANTED = {
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
}


def fetch_overpass(query: str) -> dict:
    print("Querying Overpass API...")
    r = requests.post(OVERPASS_URL, data={"data": query}, timeout=90)
    r.raise_for_status()
    return r.json()


def extract_number(tags: dict) -> str | None:
    """Try to pull a building number out of OSM tags."""
    for field in REF_FIELDS:
        val = tags.get(field, "")
        # Direct match: "32", "E14", "NW35" etc.
        if val.upper() in WANTED:
            return val.upper()
        # Try regex extraction
        for m in BLDG_NUM_RE.finditer(val.upper()):
            candidate = m.group(1)
            if candidate in WANTED:
                return candidate
    return None


def centroid_from_element(el: dict) -> tuple[float, float] | None:
    """Return (lat, lng) from an Overpass element with center."""
    c = el.get("center")
    if c:
        return c["lat"], c["lon"]
    # nodes have lat/lon directly
    if el.get("lat"):
        return el["lat"], el["lon"]
    return None


def main():
    data = fetch_overpass(QUERY)
    elements = data.get("elements", [])
    print(f"Got {len(elements)} elements from Overpass.")

    matched: dict[str, dict] = {}
    unmatched = []

    for el in elements:
        tags = el.get("tags", {})
        num = extract_number(tags)
        coords = centroid_from_element(el)
        if not coords:
            continue

        lat, lng = coords
        name = tags.get("name", f"Building {num or '?'}")

        if num and num not in matched:
            matched[num] = {"lat": round(lat, 6), "lng": round(lng, 6), "name": name}
        elif num is None:
            unmatched.append({"name": name, "lat": lat, "lng": lng, "tags": tags})

    print(f"\nMatched {len(matched)} / {len(WANTED)} wanted buildings.")
    missing = WANTED - set(matched.keys())
    if missing:
        print(f"Still missing: {sorted(missing)}")

    # Write JS output
    lines = ["// MIT building coordinates — generated from OpenStreetMap Overpass API",
             f"// Query date: {time.strftime('%Y-%m-%d')}",
             "// Bounding box: " + BBOX,
             "",
             "const BUILDING_COORDS = {"]
    for num in sorted(matched, key=lambda x: (re.sub(r'\d', '', x), int(re.sub(r'\D', '', x) or 0))):
        b = matched[num]
        lines.append(f'  "{num}": {{ lat: {b["lat"]}, lng: {b["lng"]}, name: "{b["name"]}" }},')
    lines += ["};", ""]

    with open("buildings_osm.js", "w") as f:
        f.write("\n".join(lines))
    print("\nWrote buildings_osm.js")

    # Write unmatched for review
    with open("buildings_osm_unmatched.txt", "w") as f:
        for u in unmatched:
            f.write(f"{u['name']} ({u['lat']:.5f}, {u['lng']:.5f})\n")
            for k, v in u["tags"].items():
                f.write(f"  {k}: {v}\n")
            f.write("\n")
    print(f"Wrote {len(unmatched)} unmatched buildings to buildings_osm_unmatched.txt")


if __name__ == "__main__":
    main()
