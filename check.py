"""Step 5: the project's check. Recount the headline numbers from the raw API file with plain Python (json, csv, statistics:
no pandas, no analyze.py) and require every one to equal what analyze.py wrote to results/.

    ./venv/bin/python check.py
"""
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
R = HERE / "results"
SCI = ("Physics", "Chemistry", "Physiology or Medicine")


def table(name):
    return list(csv.DictReader(open(R / name)))


def main():
    raw = json.load(open(HERE / "data" / "raw" / "laureates.json"))["laureates"]
    rows = []                                                 # (id, name, person?, gender, birth year, birth country, year, category, based)
    for l in raw:
        person = "orgName" not in l
        bplace = (l["birth"]["place"] if person else {}) if person and "place" in l.get("birth", {}) else {}
        for p in l["nobelPrizes"]:
            based = next((a["countryNow"]["en"] for a in p.get("affiliations", []) if "countryNow" in a), None)
            rows.append((l["id"], (l["knownName"] if person else l["orgName"])["en"], person, l.get("gender"),
                         int(l["birth"]["year"]) if person and l["birth"].get("year") else None,
                         bplace.get("countryNow", {}).get("en"), int(p["awardYear"]), p["category"]["en"], based))
    persons = [r for r in rows if r[2]]
    decade = lambda y: y // 10 * 10
    n = 0

    def same(label, got, want):
        nonlocal n
        n += 1
        assert got == want, f"{label}: recount {got!r} != results {want!r}"

    s = json.load(open(R / "summary.json"))
    same("laureates", len(raw), s["laureates"])
    same("prizes", len(rows), s["prizes"])
    same("people", sum(1 for l in raw if "orgName" not in l), s["people"])
    same("organizations", sum(1 for l in raw if "orgName" in l), s["organizations"])
    g = {r["gender"]: int(r["prizes"]) for r in table("gender.csv")}
    same("men", sum(1 for r in persons if r[3] == "male"), g["male"])
    same("women", sum(1 for r in persons if r[3] == "female"), g["female"])
    for r in table("birth_country.csv"):
        same("born in " + r["birth_country"], sum(1 for p in persons if p[5] == r["birth_country"]), int(r["prizes"]))

    for r in table("us_by_decade.csv"):                       # US-born by decade, and where the science laureates worked
        dec = int(r["decade"])
        pd_ = [p for p in persons if decade(p[6]) == dec]
        sci = [p for p in pd_ if p[7] in SCI and p[8]]
        us = [p for p in sci if p[8] == "USA"]
        same(f"{dec} persons", len(pd_), int(r["persons"]))
        same(f"{dec} born US", sum(1 for p in pd_ if p[5] == "USA"), int(r["born_us"]))
        same(f"{dec} science with affiliation", len(sci), int(r["sci_with_affiliation"]))
        same(f"{dec} science based US", len(us), int(r["sci_based_us"]))
        same(f"{dec} based US foreign-born", sum(1 for p in us if p[5] != "USA"), int(r["sci_based_us_foreign_born"]))

    cell = defaultdict(lambda: [0, 0])
    for p in persons:
        c = cell[(decade(p[6]), p[7])]
        c[0] += 1
        c[1] += p[3] == "female"
    for r in table("women.csv"):
        same(f"women {r['decade']} {r['category']}", cell[(int(r["decade"]), r["category"])], [int(r["laureates"]), int(r["women"])])
    same("first woman", min((p[6], p[1], p[7]) for p in persons if p[3] == "female"), (1903, "Marie Curie", "Physics"))

    cnt = Counter(r[0] for r in rows)
    same("multiple winners", sorted((r[1], r[6]) for r in rows if cnt[r[0]] > 1),
         sorted((r["name"], int(r["award_year"])) for r in table("multiple.csv")))

    ages = defaultdict(list)
    for p in persons:
        ages[(decade(p[6]), p[7])].append(p[6] - p[4])
    for r in table("age.csv"):
        for cat, v in r.items():
            if cat != "decade" and v != "":
                same(f"median age {r['decade']} {cat}", round(statistics.median(ages[(int(r["decade"]), cat)]), 1), float(v))

    per = Counter((r[6], r[7]) for r in rows if r[7] in SCI)  # laureates per science prize
    for r in table("team_size.csv"):
        prizes = [k for k in per if decade(k[0]) == int(r["decade"])]
        same(f"{r['decade']} prizes", len(prizes), int(r["prizes"]))
        same(f"{r['decade']} mean laureates", round(sum(per[k] for k in prizes) / len(prizes), 2), float(r["mean_laureates"]))
    print(f"check.py: {n} recounts agree with results/")


if __name__ == "__main__":
    main()
