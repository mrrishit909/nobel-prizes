"""Steps 2-4: one row per laureate-prize, then the questions.

    ./venv/bin/python analyze.py
        -> results/prizes.csv  summary.json  gender.csv  birth_country.csv  us_by_decade.csv  women.csv  multiple.csv  age.csv  team_size.csv
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
SCIENCE = ["Physics", "Chemistry", "Physiology or Medicine"]
CATS = SCIENCE + ["Economic Sciences", "Literature", "Peace"]


def tidy():
    """Step 2. One row per prize a laureate received. Countries are today's names ('countryNow'), so Prussia and
    Austria-Hungary don't split a country's count; 'based' is the first affiliation listed for the prize."""
    rows = []
    for l in json.load(open(HERE / "data" / "raw" / "laureates.json"))["laureates"]:
        person = "orgName" not in l
        place = (l.get("birth") or l.get("founded") or {}).get("place", {})
        for p in l["nobelPrizes"]:
            aff = next((a["countryNow"]["en"] for a in p.get("affiliations", []) if a.get("countryNow")), None)
            num, _, den = p["portion"].partition("/")                 # "1" for an unshared prize, else "1/2", "1/3", "1/4"
            rows.append({
                "laureate_id": int(l["id"]), "name": (l["knownName"] if person else l["orgName"])["en"],
                "kind": "person" if person else "organization", "gender": l.get("gender"),
                "birth_year": int(l["birth"]["year"]) if person and l["birth"].get("year") else None,
                "birth_country": place.get("countryNow", {}).get("en") if person else None,
                "award_year": int(p["awardYear"]), "category": p["category"]["en"], "portion": int(num) / int(den or 1),
                "status": p["prizeStatus"], "based_country": aff})
    d = pd.DataFrame(rows)
    d["decade"] = d["award_year"] // 10 * 10
    d["age"] = d["award_year"] - d["birth_year"]                      # +/- 1 year: the API gives the birth year reliably, not always the day
    d["n_laureates"] = d.groupby(["award_year", "category"])["laureate_id"].transform("count")
    return d


def main():
    R.mkdir(exist_ok=True)
    d = tidy()
    d.to_csv(R / "prizes.csv", index=False)
    people = d[d["kind"] == "person"]
    summary = {"laureates": int(d["laureate_id"].nunique()), "people": int(people["laureate_id"].nunique()),
               "organizations": int(d.loc[d["kind"] == "organization", "laureate_id"].nunique()), "prizes": len(d),
               "first_year": int(d["award_year"].min()), "last_year": int(d["award_year"].max())}
    (R / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Q1 who: gender and birth country (people only; organisations have neither)
    g = people["gender"].value_counts().rename_axis("gender").reset_index(name="prizes")
    g["pct"] = (100 * g["prizes"] / g["prizes"].sum()).round(1)
    g.to_csv(R / "gender.csv", index=False)
    bc = people["birth_country"].value_counts().head(12).rename_axis("birth_country").reset_index(name="prizes")
    bc["pct"] = (100 * bc["prizes"] / len(people)).round(1)
    bc.to_csv(R / "birth_country.csv", index=False)

    # Q2 which decade was most American? by birthplace (all prizes to people), and by where science laureates worked
    sci = d[d["category"].isin(SCIENCE) & d["based_country"].notna()]
    by = pd.DataFrame({
        "persons": people.groupby("decade").size(),
        "born_us": people[people["birth_country"] == "USA"].groupby("decade").size(),
        "sci_with_affiliation": sci.groupby("decade").size(),
        "sci_based_us": sci[sci["based_country"] == "USA"].groupby("decade").size(),
        "sci_based_us_foreign_born": sci[(sci["based_country"] == "USA") & (sci["birth_country"] != "USA")].groupby("decade").size(),
    }).fillna(0).astype(int).reset_index()
    by["born_us_pct"] = (100 * by["born_us"] / by["persons"]).round(1)
    by["based_us_pct"] = (100 * by["sci_based_us"] / by["sci_with_affiliation"]).round(1)
    by["foreign_born_pct_of_us_based"] = (100 * by["sci_based_us_foreign_born"] / by["sci_based_us"].where(by["sci_based_us"] > 0)).round(1)
    by.to_csv(R / "us_by_decade.csv", index=False)

    # Q3 women: share by decade and category; the first woman
    women = people.assign(woman=people["gender"] == "female")
    w = women.groupby(["decade", "category"]).agg(laureates=("woman", "size"), women=("woman", "sum")).reset_index()
    w["pct"] = (100 * w["women"] / w["laureates"]).round(1)
    w.to_csv(R / "women.csv", index=False)

    # Q4 more than one prize
    m = d.groupby("laureate_id").filter(lambda x: len(x) > 1).sort_values(["name", "award_year"])
    m[["name", "kind", "award_year", "category"]].to_csv(R / "multiple.csv", index=False)

    # Q5 how old, and how many share a prize (the three science prizes)
    age = people[people["category"].isin(CATS)].groupby(["decade", "category"])["age"].median().unstack().reindex(columns=CATS)
    age.round(1).reset_index().to_csv(R / "age.csv", index=False)
    pz = d[d["category"].isin(SCIENCE)].drop_duplicates(["award_year", "category"])
    t = pz.groupby(["decade", "n_laureates"]).size().unstack(fill_value=0).reset_index()
    t["prizes"] = t[[1, 2, 3]].sum(axis=1)
    t["mean_laureates"] = ((t[1] + 2 * t[2] + 3 * t[3]) / t["prizes"]).round(2)
    t.columns = [str(c) for c in t.columns]
    t.rename(columns={"1": "alone", "2": "two", "3": "three"}).to_csv(R / "team_size.csv", index=False)

    first = women[women["woman"]].sort_values("award_year").iloc[0]
    print(g.to_string(index=False)); print(bc.head(5).to_string(index=False)); print(by.to_string(index=False))
    print("first woman:", first["name"], first["category"], first["award_year"])
    hi = w[w["laureates"] >= 5].sort_values("pct", ascending=False).head(3); print(hi.to_string(index=False))
    print(m[["name", "award_year", "category"]].to_string(index=False)); print(age.round(0).to_string())
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
