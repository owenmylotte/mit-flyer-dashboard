# Scripts

## assign_stewards_by_dept.py

Assigns stewards to posting spots in the tracker CSV.

**How it works:**
1. Reads steward names from the CSV's "Assigned To" column
2. Queries MIT LDAP (`ldap.mit.edu`) for each steward's department (`ou` field)
3. Uses the `BUILDING_TO_DEPTS` map to find which department(s) each building belongs to
4. Divides spots in each building evenly (round-robin) among stewards in that department
5. Falls back to geographic nearest-neighbor for buildings with no matching steward

**Run:**
```bash
python assign_stewards_by_dept.py \
    --csv  ../mit_flyer_tracker_full.csv \
    --out  ../mit_flyer_tracker_full.csv
```

The `--out` can be the same file — it re-derives all assignments from scratch each run.

**When to re-run:** Any time the steward roster changes (new steward added,
someone leaves). Update the "Assigned To" column in the Google Sheet to match
the names in the CSV, then re-run.

**14 stewards not in LDAP:** These are likely non-MIT-account holders or
people who have left. They receive 0 assignments and must be handled manually.
The 496 spots are fully covered by the remaining 72 stewards.

---

## fetch_mit_buildings_osm.py

One-time script to fetch accurate building coordinates from the
OpenStreetMap Overpass API. Outputs `buildings_osm.js` which can
replace the `BUILDING_COORDS` object in `index.html`.

**Run:**
```bash
pip install requests
python fetch_mit_buildings_osm.py
```
