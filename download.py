"""Step 1: every Nobel laureate from the official Nobel Prize API (v2.1), prizes 1901 to the latest year.

    ./venv/bin/python download.py   -> data/raw/laureates.json (not committed), results/pull.json
"""
import json
import ssl
import urllib.request
from datetime import date
from pathlib import Path

import certifi

HERE = Path(__file__).parent
URL = "https://api.nobelprize.org/2.1/laureates?limit=2000&format=json"
CTX = ssl.create_default_context(cafile=certifi.where())


def main():
    (HERE / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (HERE / "results").mkdir(exist_ok=True)
    raw = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 research-portfolio"}),
                                 context=CTX, timeout=120).read()
    data = json.loads(raw)
    assert data["meta"]["count"] == len(data["laureates"]), "the API paged: raise limit"
    (HERE / "data" / "raw" / "laureates.json").write_bytes(raw)
    prizes = [p for l in data["laureates"] for p in l["nobelPrizes"]]
    meta = {"pulled": date.today().isoformat(), "laureates": len(data["laureates"]), "prizes": len(prizes),
            "first_year": min(int(p["awardYear"]) for p in prizes), "last_year": max(int(p["awardYear"]) for p in prizes)}
    (HERE / "results" / "pull.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(meta)


if __name__ == "__main__":
    main()
