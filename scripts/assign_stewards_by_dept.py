#!/usr/bin/env python3
"""
MIT Flyer Dashboard — Steward Assignment Generator
===================================================
Assigns stewards to posting spots by:
  1. Querying MIT LDAP to find each steward's department (ou field).
  2. Mapping each building to its primary department(s).
  3. Dividing spots in each building evenly among stewards in that dept.
  4. Falling back to geographic nearest-neighbor (KNN) for any spots
     whose building has no matching steward.

Usage
-----
    python assign_stewards_by_dept.py \
        --csv  ../mit_flyer_tracker_full.csv \
        --out  ../mit_flyer_tracker_full.csv   # safe to overwrite

The script is idempotent — re-running after a roster change (steward
added/removed) will re-derive all assignments from scratch.

Dependencies: stdlib only (subprocess, csv, math, collections).
"""

import argparse
import csv
import math
import subprocess
from collections import defaultdict

# ─── MIT LDAP ──────────────────────────────────────────────────────────────

LDAP_HOST = "ldap://ldap.mit.edu:389"
LDAP_BASE = "dc=mit,dc=edu"

# MIT stores department as either full name ("PHYSICS") or course number ("8").
# Map numeric course codes → canonical department string.
COURSE_NUM_TO_DEPT: dict[str, str] = {
    "1":  "CIVIL AND ENVIRONMENTAL ENG",
    "2":  "MECHANICAL ENGINEERING",
    "3":  "MATERIALS SCIENCE AND ENG.",
    "4":  "ARCHITECTURE",
    "5":  "CHEMISTRY",
    "6":  "ELECTRICAL ENG & COMPUTER SCI",
    "7":  "BIOLOGY",
    "8":  "PHYSICS",
    "9":  "BRAIN AND COGNITIVE SCIENCES",
    "10": "CHEMICAL ENGINEERING",
    "11": "URBAN STUDIES AND PLANNING",
    "12": "EARTH, ATMOS & PLANETARY SCI",
    "14": "ECONOMICS",
    "15": "MANAGEMENT",
    "16": "AERONAUTICS AND ASTRONAUTICS",
    "17": "POLITICAL SCIENCE",
    "18": "MATHEMATICS",
    "20": "BIOLOGICAL ENGINEERING",
    "22": "NUCLEAR ENGINEERING",
    "STS": "SCIENCE TECHNOLOGY & SOCIETY",
    "HSTS": "SCIENCE TECHNOLOGY & SOCIETY",
}

# Aliases so variant LDAP spellings map to the same key used in BUILDING_TO_DEPT.
DEPT_ALIAS: dict[str, str] = {
    "EARTH, ATMOS & PLANETARY SCI":      "EAPS",
    "ELECTRICAL ENG & COMPUTER SCI":     "EECS",
    "CIVIL AND ENVIRONMENTAL ENG":       "CEE",
    "MATERIALS SCIENCE AND ENG.":        "DMSE",
    "AERONAUTICS AND ASTRONAUTICS":      "AERO",
    "BIOLOGICAL ENGINEERING":            "BE",
    "BRAIN AND COGNITIVE SCIENCES":      "BCS",
    "CHEMICAL ENGINEERING":              "CHEME",
    "CHEMISTRY":                         "CHEM",
    "MECHANICAL ENGINEERING":            "MECHE",
    "NUCLEAR ENGINEERING":               "NSE",
    "URBAN STUDIES AND PLANNING":        "DUSP",
    "SCIENCE TECHNOLOGY & SOCIETY":      "STS",
    "LINGUISTICS & PHILOSOPHY":          "LING",
    "POLITICAL SCIENCE":                 "POLSCI",
    "OPERATIONS RESEARCH":               "IDSS",
    "MANAGEMENT":                        "SLOAN",
    "ECONOMICS":                         "ECON",
    "MATHEMATICS":                       "MATH",
    "PHYSICS":                           "PHYS",
    "BIOLOGY":                           "BIO",
    "ARCHITECTURE":                      "ARCH",
}


def ldap_lookup_dept(name: str) -> str | None:
    """Return normalized department key for a person, or None if not found."""
    try:
        result = subprocess.run(
            ["ldapsearch", "-x", "-H", LDAP_HOST, "-b", LDAP_BASE,
             f"(cn={name})", "ou"],
            capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    ou_val = None
    for line in result.stdout.splitlines():
        if line.startswith("ou:"):
            ou_val = line.split(":", 1)[1].strip()
            break

    if ou_val is None:
        return None

    # Numeric course code → full name first
    ou_val = COURSE_NUM_TO_DEPT.get(ou_val, ou_val)
    # Then alias to canonical short key
    return DEPT_ALIAS.get(ou_val, ou_val.upper())


# ─── BUILDING → DEPARTMENT MAP ─────────────────────────────────────────────
# Maps MIT building number → list of department keys (ordered by primary dept).
# A building can belong to multiple depts; stewards from ALL listed depts share
# those spots.  Adjust this dict as departments move buildings.

BUILDING_TO_DEPTS: dict[str, list[str]] = {
    # ── Main campus numbered buildings ──────────────────────────────────────
    "1":   ["CEE"],
    "2":   ["MATH"],
    "3":   ["MECHE"],
    "4":   ["DMSE", "CHEM"],
    "5":   ["CHEM"],
    "6":   ["PHYS"],
    "6C":  ["PHYS"],
    "7":   ["ARCH"],
    "7A":  ["ARCH"],
    "8":   ["PHYS", "DMSE"],
    "9":   ["DUSP", "LING"],
    "10":  ["ARCH", "DUSP"],
    "11":  ["LING", "DUSP"],
    "12":  ["EAPS"],
    "13":  ["DMSE"],
    "14":  ["LING", "STS"],
    "16":  ["DMSE"],
    "17":  ["PHYS"],
    "18":  ["CHEM"],
    "24":  ["NSE", "EAPS"],
    "26":  ["PHYS"],
    "31":  ["AERO"],
    "32":  ["EECS", "LING"],
    "33":  ["AERO"],
    "34":  ["EECS"],
    "35":  ["AERO", "MECHE"],
    "36":  ["EECS"],
    "37":  ["EECS", "CEE"],
    "38":  ["EECS"],
    "39":  ["AERO"],
    "41":  ["AERO"],
    "42":  ["AERO"],
    "43":  ["AERO"],
    "45":  ["EECS", "IDSS"],
    "46":  ["BCS"],
    "48":  ["NSE", "CEE"],
    "50":  ["ARCH"],          # Walker Memorial — common space, assign to ARCH
    "51":  ["EECS"],
    "54":  ["EAPS", "CHEME"],
    "56":  ["BE"],
    "57":  ["BE"],
    "62":  ["EECS"],
    "64":  ["EECS"],
    "66":  ["CHEME"],
    "68":  ["BIO"],
    "76":  ["BIO", "BE"],
    # ── East campus ─────────────────────────────────────────────────────────
    "E1":  ["ARCH"],
    "E2":  ["ARCH"],
    "E14": ["ARCH"],          # Media Lab
    "E15": ["ARCH"],          # Wiesner / Arts
    "E17": ["SLOAN"],         # Admissions/admin
    "E18": ["SLOAN"],
    "E19": ["SLOAN"],
    "E23": ["BIO"],
    "E25": ["BIO"],
    "E28": ["ARCH"],          # MIT Museum
    "E37": ["EAPS"],
    "E38": ["EAPS"],
    "E39": ["EAPS"],
    "E40": ["BIO"],
    "E48": ["IDSS"],
    "E51": ["SLOAN", "STS"],
    "E52": ["SLOAN"],
    "E53": ["POLSCI", "ECON"],
    "E55": ["SLOAN"],
    "E60": ["POLSCI", "SLOAN"],
    "E62": ["SLOAN", "IDSS"],
    "E70": ["SLOAN"],
    "E90": ["SLOAN"],
    "E94": ["SLOAN"],
    # ── North campus ────────────────────────────────────────────────────────
    "N9":  ["NSE"],
    "N10": ["NSE"],
    "N42": ["BIO"],
    "N51": ["BIO"],
    "N52": ["BIO"],
    "N57": ["BIO"],
    # ── Northeast campus ────────────────────────────────────────────────────
    "NE18": ["MECHE"],
    "NE36": ["MECHE"],
    "NE46": ["MECHE"],
    "NE47": ["MECHE"],
    "NE48": ["MECHE"],
    "NE49": ["MECHE"],
    "NE55": ["MECHE"],
    "NE83": ["MECHE", "AERO"],
    "NE103":["MECHE"],
    # ── Northwest campus ────────────────────────────────────────────────────
    "NW10": ["PHYS"],
    "NW12": ["NSE"],
    "NW13": ["NSE"],
    "NW14": ["PHYS"],         # Magnet Lab
    "NW17": ["NSE"],
    "NW21": ["NSE"],
    "NW22": ["NSE"],
    "NW23": ["NSE"],
    "NW30": ["NSE"],
    "NW35": ["MECHE"],        # Edgerton Center
    "NW61": ["NSE"],
    "NW86": ["NSE"],
    "NW98": ["NSE"],
    # ── West campus ─────────────────────────────────────────────────────────
    "W2":  ["ARCH"],
    "W5":  ["ARCH"],
    "W8":  ["ARCH"],
    "W11": ["ARCH"],
    "W13": ["ARCH"],
    "W15": ["ARCH"],
    "W16": ["ARCH"],          # Kresge
    "W18": ["ARCH"],
    "W20": ["DUSP"],          # Student Center — assign to DUSP (common/admin)
    "W31": ["MECHE"],         # du Pont Gym — MechE has many athletes
    "W32": ["MECHE"],
    "W35": ["MECHE"],
    "W41": ["MECHE"],
    "W46": ["DUSP"],
    "W59": ["DUSP"],
    "W84": ["DUSP"],
    "W89": ["DUSP"],
    "W91": ["DUSP"],
    "W92": ["DUSP"],
    "W97": ["DUSP"],
    "W98": ["DUSP"],
    "WW15":["DUSP"],
}

# ─── BUILDING COORDINATES (for geographic fallback) ─────────────────────────

COORDS: dict[str, tuple[float, float]] = {
    "1":(42.3596,-71.0942),"2":(42.3598,-71.0928),"3":(42.3594,-71.0934),
    "4":(42.3598,-71.0919),"5":(42.3594,-71.0948),"6":(42.3602,-71.0924),
    "6C":(42.3603,-71.0922),"7":(42.3592,-71.0936),"7A":(42.3591,-71.0935),
    "8":(42.3602,-71.0914),"9":(42.3592,-71.0907),"10":(42.3594,-71.0927),
    "11":(42.359,-71.092),"12":(42.3588,-71.0924),"13":(42.3593,-71.0916),
    "14":(42.359,-71.0903),"16":(42.3602,-71.0908),"17":(42.3604,-71.0902),
    "18":(42.3598,-71.0903),"24":(42.3601,-71.0897),"26":(42.3605,-71.0912),
    "31":(42.36,-71.0935),"32":(42.3616,-71.0906),"33":(42.3598,-71.0938),
    "34":(42.3607,-71.093),"35":(42.3604,-71.0935),"36":(42.3604,-71.092),
    "37":(42.3601,-71.0924),"38":(42.3605,-71.0928),"39":(42.36,-71.093),
    "41":(42.3597,-71.0945),"42":(42.3595,-71.0947),"43":(42.3593,-71.0949),
    "45":(42.3619,-71.0915),"46":(42.3621,-71.0907),"48":(42.3618,-71.0902),
    "50":(42.3587,-71.0899),"51":(42.3589,-71.0904),"54":(42.3601,-71.0912),
    "56":(42.3608,-71.0908),"57":(42.361,-71.0906),"62":(42.3601,-71.088),
    "64":(42.3604,-71.0877),"66":(42.3609,-71.0916),"68":(42.3612,-71.092),
    "76":(42.3615,-71.0925),
    "E1":(42.3596,-71.0865),"E2":(42.3598,-71.0867),"E14":(42.3603,-71.0872),
    "E15":(42.3607,-71.0876),"E17":(42.3604,-71.087),"E18":(42.3605,-71.0865),
    "E19":(42.3607,-71.0863),"E23":(42.3609,-71.0858),"E25":(42.3608,-71.0848),
    "E28":(42.3622,-71.0862),"E37":(42.36,-71.084),"E38":(42.3602,-71.0838),
    "E39":(42.3604,-71.0836),"E40":(42.3614,-71.086),"E48":(42.3616,-71.0852),
    "E51":(42.361,-71.0845),"E52":(42.3613,-71.0835),"E53":(42.3612,-71.0838),
    "E55":(42.3615,-71.084),"E60":(42.3618,-71.0832),"E62":(42.3617,-71.083),
    "E70":(42.362,-71.0825),"E90":(42.3625,-71.085),"E94":(42.3627,-71.0845),
    "N9":(42.364,-71.088),"N10":(42.3642,-71.0882),"N42":(42.3638,-71.0895),
    "N51":(42.3645,-71.089),"N52":(42.3647,-71.0892),"N57":(42.365,-71.0888),
    "NE18":(42.3655,-71.0865),"NE36":(42.3658,-71.087),"NE46":(42.366,-71.0868),
    "NE47":(42.3662,-71.0866),"NE48":(42.3664,-71.0864),"NE49":(42.3666,-71.0862),
    "NE55":(42.3668,-71.086),"NE83":(42.367,-71.0875),"NE103":(42.3672,-71.088),
    "NW10":(42.3628,-71.0955),"NW12":(42.363,-71.0958),"NW13":(42.3632,-71.096),
    "NW14":(42.3634,-71.0962),"NW17":(42.3636,-71.0965),"NW21":(42.3638,-71.097),
    "NW22":(42.364,-71.0972),"NW23":(42.3642,-71.0974),"NW30":(42.3644,-71.0976),
    "NW35":(42.3632,-71.0968),"NW61":(42.3646,-71.0978),"NW86":(42.3648,-71.098),
    "NW98":(42.365,-71.0982),
    "W2":(42.3575,-71.0935),"W5":(42.3572,-71.094),"W8":(42.357,-71.0945),
    "W11":(42.3568,-71.095),"W13":(42.3566,-71.0955),"W15":(42.3564,-71.096),
    "W16":(42.358,-71.096),"W18":(42.3562,-71.0965),"W20":(42.3573,-71.0957),
    "W31":(42.3567,-71.0975),"W32":(42.3569,-71.0978),"W35":(42.3568,-71.097),
    "W41":(42.3565,-71.098),"W46":(42.3573,-71.0995),"W59":(42.356,-71.099),
    "W84":(42.3558,-71.1),"W89":(42.3556,-71.1005),"W91":(42.3554,-71.101),
    "W92":(42.3552,-71.1012),"W97":(42.355,-71.1015),"W98":(42.3548,-71.1018),
    "WW15":(42.3546,-71.102),
}


def dist(b1: str, b2: str) -> float:
    c1, c2 = COORDS.get(b1), COORDS.get(b2)
    if not c1 or not c2:
        return float("inf")
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])


# ─── CORE LOGIC ────────────────────────────────────────────────────────────

def lookup_all_depts(names: list[str]) -> dict[str, str | None]:
    """LDAP-query every steward name. Returns {name: dept_key or None}."""
    result = {}
    total = len(names)
    for i, name in enumerate(names, 1):
        print(f"  [{i}/{total}] {name} ...", end=" ", flush=True)
        dept = ldap_lookup_dept(name)
        print(dept or "(not found)")
        result[name] = dept
    return result


def assign(spots: list[dict], steward_depts: dict[str, str | None]) -> list[dict]:
    """
    Assign each spot to a steward.

    Pass 1 — departmental: for each building, find stewards whose dept
              matches that building's primary dept(s). Divide spots in
              that building evenly across those stewards (round-robin by
              floor then spot index to keep assignments contiguous).

    Pass 2 — geographic KNN: any spot still unassigned gets the nearest
              steward (by building coordinate) who still has capacity.
    """
    # Build dept → [steward names] index
    dept_to_stewards: dict[str, list[str]] = defaultdict(list)
    for name, dept in steward_depts.items():
        if dept:
            dept_to_stewards[dept].append(name)

    # Capacity: ceil(total / num_stewards) + 2 buffer so nobody is stranded
    num_stewards = len(steward_depts)
    base_cap = math.ceil(len(spots) / max(num_stewards, 1)) + 2
    capacity: dict[str, int] = {n: base_cap for n in steward_depts}

    # Steward → representative building coordinate for KNN fallback
    # Use the first building in BUILDING_TO_DEPTS whose dept matches theirs.
    def steward_building(name: str) -> str | None:
        dept = steward_depts.get(name)
        if not dept:
            return None
        for bldg, depts in BUILDING_TO_DEPTS.items():
            if dept in depts:
                return bldg
        return None

    # Group spots by building, preserving original row order
    by_building: dict[str, list[int]] = defaultdict(list)
    for i, spot in enumerate(spots):
        by_building[spot["Bldg #"]].append(i)

    assigned_count: dict[str, int] = defaultdict(int)

    # ── Pass 1: departmental assignment ────────────────────────────────────
    for bldg, idxs in by_building.items():
        depts_for_bldg = BUILDING_TO_DEPTS.get(bldg, [])
        # Collect stewards eligible for this building (any matching dept)
        eligible = []
        for dept in depts_for_bldg:
            for s in dept_to_stewards.get(dept, []):
                if s not in eligible:
                    eligible.append(s)

        if not eligible:
            continue  # handled in pass 2

        # Round-robin across eligible stewards, in original spot order
        for i, idx in enumerate(idxs):
            steward = eligible[i % len(eligible)]
            if capacity[steward] > 0:
                spots[idx]["Assigned To"] = steward
                capacity[steward] -= 1
                assigned_count[steward] += 1

    # ── Pass 2: geographic KNN for remaining unassigned spots ───────────────
    unassigned = [i for i, s in enumerate(spots) if not s.get("Assigned To", "").strip()]
    if unassigned:
        print(f"\n  Pass 2: assigning {len(unassigned)} spots without dept match via KNN...")

    for idx in unassigned:
        bldg = spots[idx]["Bldg #"]
        # Find steward with remaining capacity closest to this building
        candidates = [(name, steward_building(name)) for name, cap in capacity.items() if cap > 0]
        if not candidates:
            print(f"    WARNING: no capacity left for spot {idx} in bldg {bldg}")
            continue
        best = min(candidates, key=lambda nc: dist(bldg, nc[1]) if nc[1] else float("inf"))
        spots[idx]["Assigned To"] = best[0]
        capacity[best[0]] -= 1
        assigned_count[best[0]] += 1

    return spots


def print_summary(steward_depts: dict[str, str | None], spots: list[dict]) -> None:
    counts: dict[str, int] = defaultdict(int)
    for s in spots:
        name = s.get("Assigned To", "").strip()
        if name:
            counts[name] += 1

    print(f"\n{'Steward':<35} {'Dept':<10} {'Spots':>5}")
    print("─" * 53)
    for name in sorted(counts, key=lambda n: -counts[n]):
        dept = steward_depts.get(name) or "—"
        print(f"  {name:<33} {dept:<10} {counts[name]:>5}")

    unassigned = sum(1 for s in spots if not s.get("Assigned To", "").strip())
    print(f"\nTotal spots: {len(spots)}  |  Unassigned: {unassigned}")


# ─── MAIN ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Tracker CSV (input)")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    # Load CSV
    with open(args.csv, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        spots = [dict(row) for row in reader]

    # Clear existing assignments so we start fresh
    for s in spots:
        s["Assigned To"] = ""

    # Collect unique steward names from the original "Assigned To" column.
    # Re-read so we have the original names before we wiped them.
    with open(args.csv, newline="") as f:
        orig = list(csv.DictReader(f))
    steward_names = sorted({
        r["Assigned To"].strip()
        for r in orig
        if r.get("Assigned To", "").strip()
    })

    print(f"Found {len(steward_names)} stewards. Looking up departments via MIT LDAP...\n")
    steward_depts = lookup_all_depts(steward_names)

    print(f"\nRunning assignment...")
    spots = assign(spots, steward_depts)

    # Write output
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(spots)

    print(f"\nWrote {len(spots)} rows → {args.out}")
    print_summary(steward_depts, spots)


if __name__ == "__main__":
    main()
