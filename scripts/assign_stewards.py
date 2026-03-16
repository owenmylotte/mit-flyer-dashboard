#!/usr/bin/env python3
"""
Procedural steward-to-spot assignment generator.

Reads the current tracker CSV and a steward roster, then assigns
stewards to unassigned spots using a geographic cluster + capacity
algorithm. Outputs a new CSV with the "Assigned To" column filled in.

Strategy
--------
1. Group spots by building.
2. For each steward, specify their home buildings or campus region.
   Stewards get assigned to spots in buildings near their "home" first.
3. Balance load: each steward gets at most `max_spots` spots (default: 15).
4. If a building has no steward claiming it, assign whoever has capacity
   and is geographically closest.

Usage
-----
    pip install pandas
    python assign_stewards.py \
        --csv  ../mit_flyer_tracker_full.csv \
        --roster steward_roster.csv \
        --out   ../mit_flyer_tracker_assigned.csv

Steward roster CSV columns
--------------------------
    name, department, home_buildings (semicolon-separated bldg nums), max_spots
    Example row:
        Robert van der Drift, EAPS, 54;24;12;17, 60

If home_buildings is empty, the steward is treated as a "floater" and
fills in remaining spots after all primary assignments are done.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Building coordinates (used for geographic fallback assignment).
# Keep in sync with index.html / buildings_data.js.
# ---------------------------------------------------------------------------
COORDS: dict[str, tuple[float, float]] = {
    "1":(42.3596,-71.0942),"2":(42.3598,-71.0928),"3":(42.3594,-71.0934),
    "4":(42.3598,-71.0919),"5":(42.3594,-71.0948),"6":(42.3602,-71.0924),
    "6C":(42.3603,-71.0922),"7":(42.3592,-71.0936),"8":(42.3602,-71.0914),
    "9":(42.3592,-71.0907),"10":(42.3594,-71.0927),"11":(42.359,-71.092),
    "12":(42.3588,-71.0924),"13":(42.3593,-71.0916),"14":(42.359,-71.0903),
    "16":(42.3602,-71.0908),"17":(42.3604,-71.0902),"18":(42.3598,-71.0903),
    "24":(42.3601,-71.0897),"26":(42.3605,-71.0912),"31":(42.36,-71.0935),
    "32":(42.3616,-71.0906),"33":(42.3598,-71.0938),"34":(42.3607,-71.093),
    "35":(42.3604,-71.0935),"36":(42.3604,-71.092),"37":(42.3601,-71.0924),
    "38":(42.3605,-71.0928),"39":(42.36,-71.093),"41":(42.3597,-71.0945),
    "42":(42.3595,-71.0947),"43":(42.3593,-71.0949),"45":(42.3619,-71.0915),
    "46":(42.3621,-71.0907),"48":(42.3618,-71.0902),"50":(42.3587,-71.0899),
    "51":(42.3589,-71.0904),"54":(42.3601,-71.0912),"56":(42.3608,-71.0908),
    "57":(42.361,-71.0906),"62":(42.3601,-71.088),"64":(42.3604,-71.0877),
    "66":(42.3609,-71.0916),"68":(42.3612,-71.092),"76":(42.3615,-71.0925),
    "E14":(42.3603,-71.0872),"E15":(42.3607,-71.0876),"E17":(42.3604,-71.087),
    "E18":(42.3605,-71.0865),"E25":(42.3608,-71.0848),"E28":(42.3622,-71.0862),
    "E40":(42.3614,-71.086),"E51":(42.361,-71.0845),"E52":(42.3613,-71.0835),
    "E53":(42.3612,-71.0838),"E55":(42.3615,-71.084),"E62":(42.3617,-71.083),
    "N42":(42.3638,-71.0895),"N51":(42.3645,-71.089),"N52":(42.3647,-71.0892),
    "NW14":(42.3634,-71.0962),"NW35":(42.3632,-71.0968),
    "W16":(42.358,-71.096),"W20":(42.3573,-71.0957),"W31":(42.3567,-71.0975),
}


def dist_sq(b1: str, b2: str) -> float:
    """Squared lat/lng distance between two building numbers."""
    c1 = COORDS.get(b1)
    c2 = COORDS.get(b2)
    if not c1 or not c2:
        return float("inf")
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2


# ---------------------------------------------------------------------------


def load_roster(path: str) -> list[dict]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        roster = []
        for row in reader:
            roster.append({
                "name": row["name"].strip(),
                "department": row.get("department", "").strip(),
                "home_buildings": [b.strip() for b in row.get("home_buildings", "").split(";") if b.strip()],
                "max_spots": int(row.get("max_spots", 15)),
                "assigned": [],   # will be filled during assignment
            })
    return roster


def load_spots(csv_path: str) -> list[dict]:
    spots = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            spots.append(dict(row))
    return spots


def assign(spots: list[dict], roster: list[dict]) -> list[dict]:
    """
    Two-pass assignment:
      Pass 1 — each steward claims unassigned spots in their home buildings
               until they hit max_spots.
      Pass 2 — remaining unassigned spots go to the geographically closest
               steward that still has capacity.
    """
    # Index spots by building
    by_building: dict[str, list[int]] = defaultdict(list)
    for i, s in enumerate(spots):
        if not s.get("Assigned To", "").strip():
            by_building[s["Bldg #"]].append(i)

    # Track capacity
    capacity = {s["name"]: s["max_spots"] - len(s["assigned"]) for s in roster}
    name_to_steward = {s["name"]: s for s in roster}

    # Pass 1: primary/home building assignment
    for steward in roster:
        for bldg in steward["home_buildings"]:
            for idx in list(by_building.get(bldg, [])):
                if capacity[steward["name"]] <= 0:
                    break
                spots[idx]["Assigned To"] = steward["name"]
                by_building[bldg].remove(idx)
                steward["assigned"].append(idx)
                capacity[steward["name"]] -= 1

    # Pass 2: assign leftovers geographically
    # Collect all still-unassigned spot indices
    remaining = [i for idxs in by_building.values() for i in idxs]

    for idx in remaining:
        bldg = spots[idx]["Bldg #"]
        # Find steward with capacity closest to this building
        best = min(
            (s for s in roster if capacity[s["name"]] > 0),
            key=lambda s: min(
                (dist_sq(bldg, hb) for hb in s["home_buildings"]),
                default=float("inf"),
            ),
            default=None,
        )
        if best is None:
            print(f"WARNING: no steward with capacity left for spot {idx} in bldg {bldg}")
            continue
        spots[idx]["Assigned To"] = best["name"]
        best["assigned"].append(idx)
        capacity[best["name"]] -= 1

    return spots


def print_summary(roster: list[dict]) -> None:
    print(f"\n{'Steward':<30} {'Dept':<10} {'Spots':>5}")
    print("-" * 48)
    for s in sorted(roster, key=lambda x: -len(x["assigned"])):
        print(f"{s['name']:<30} {s['department']:<10} {len(s['assigned']):>5}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Path to tracker CSV")
    parser.add_argument("--roster", required=True, help="Path to steward roster CSV")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    roster = load_roster(args.roster)
    spots = load_spots(args.csv)

    spots = assign(spots, roster)

    # Write output
    fieldnames = list(spots[0].keys())
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(spots)

    print(f"Wrote {len(spots)} rows to {args.out}")
    print_summary(roster)

    unassigned = sum(1 for s in spots if not s.get("Assigned To", "").strip())
    if unassigned:
        print(f"\nWARNING: {unassigned} spots still have no assignment.")
    else:
        print("\nAll spots assigned.")


if __name__ == "__main__":
    main()
