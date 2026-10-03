# Who wins the Nobel Prize?

Every Nobel Prize from 1901 to 2025 is in the Nobel Foundation's free API: 1,026 prizes to 1,018 laureates (990 people and
28 organisations). This project counts what that table says:
- who wins, by gender and birthplace;
- how much of the prize is American by birth and how much by workplace;
- how few women there are, and how that is changing;
- how old laureates are, and how many people share a science prize.

The questions follow DataCamp's "Visualizing the History of Nobel Prize Winners" project; the data is the official API through
2025, not a course copy.

Build log: https://mrrishit909.github.io/projects/nobel-prizes/

## Data

Nobel Prize API v2.1 (`api.nobelprize.org/2.1/laureates`), pulled 2026-10-03. Free to use under CC0 (the API's terms).
`download.py` fetches it; the raw JSON is not committed. `results/pull.json` records the pull date and counts.

```
./venv/bin/pip install pandas matplotlib certifi      # in a venv
./venv/bin/python download.py    # data/raw/laureates.json
./venv/bin/python analyze.py     # results/*.csv, summary.json
./venv/bin/python check.py
./venv/bin/python charts.py
```

## Steps

1. **Download.** One call returns every laureate: name, gender, birthplace and, for each prize, the year, category, share
   and the institution where the laureate worked.
2. **One row per prize received** (`results/prizes.csv`, 1,026 rows). A person who won twice is two rows. Countries use today's
   names (the API's `countryNow`), so Prussia or Austria-Hungary don't split a country's count. Organisations have no
   birthplace or gender, so those figures cover the 995 prizes to people.
3. **Who:** gender and birthplace (`gender.csv`, `birth_country.csv`).
4. **Where:** the US share by decade, by birthplace and by where science laureates worked (`us_by_decade.csv`); women by
   decade and category (`women.csv`); everyone who won more than once (`multiple.csv`); median age at the award and the number
   of laureates per science prize (`age.csv`, `team_size.csv`).
5. **Check.** `check.py` recounts 255 numbers from the raw file with plain Python (json, csv, statistics) and requires
   every one to equal `results/`.
6. **Charts.**

## Results

| Born in | Prizes | Share |
|---|---|---|
| USA | 299 | 30.1% |
| United Kingdom | 95 | 9.5% |
| Germany | 84 | 8.4% |
| France | 63 | 6.3% |
| Japan | 30 | 3.0% |

- **Women** won 68 of the 995 prizes to people (6.8%). The first was Marie Curie (physics, 1903); in the 1950s none did;
  in 2020-25 it is 14 of 72 (19%).
- **The US:** 43.7% of the 2000s laureates were born there, the highest decade. In the 1990s 74% of the science laureates
  worked at a US institution, and 30% of those had been born elsewhere.
- **Age:** physics laureates' median age at the award went from 42 in the 1930s to 70 in the 2010s (chemistry 48 to 72,
  medicine 52.5 to 69).
- **Sharing:** 22 of 27 science prizes in the 1900s (81.5%) went to one person; in the 2010s 3 of 30 (10%) did and 20 (66.7%)
  were shared by three. Mean laureates per prize: 1.22, then 2.57.
- **More than one prize:** Marie Curie, Linus Pauling, John Bardeen, Frederick Sanger and K. Barry Sharpless, and two
  organisations (the Red Cross three times, the UN refugee agency twice).

## Not done, and caveats

- Age is the award year minus the birth year, so it can be off by one.
- "Worked in" is the first institution listed for the prize. Only the science prizes have one, and 5 of 662 science rows
  have none.
- The 2020s are six prize years (2020-25), so their points are noisy. The 2026 prizes are not in the data yet.
- Three prizes were not received in the usual way (Pasternak 1958 "restricted", Sartre 1964 and Le Duc Tho 1973 "declined");
  they stay in the counts.
- Nothing here says why: no institutions ranked, no nominations (sealed for 50 years), no motivations text.
