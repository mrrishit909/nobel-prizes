"""Step 6: charts.   ./venv/bin/python charts.py -> charts/00_cover.png, 01_women.png, 02_us.png, 03_age.png, 04_team.png"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
INK, DIM, GRID, BG, BLUE, ORANGE, GRAY, GREEN = "#f2f2f0", "#8a8a87", "#1d1d1d", "#0b0b0b", "#3987e5", "#d95926", "#9a9a96", "#3aa876"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": INK,
                     "axes.edgecolor": "#3a3a3a", "axes.labelcolor": DIM, "xtick.color": DIM, "ytick.color": DIM,
                     "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 1,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "font.size": 11, "axes.titlesize": 13,
                     "axes.titlelocation": "left", "axes.titlepad": 12})
LABEL = lambda d: "2020-25" if d == 2020 else f"{d}s"      # 2020s: six prize years so far


def save(fig, name):
    fig.tight_layout(); fig.savefig(HERE / "charts" / name, dpi=150); plt.close(fig)


def us(ax, big=False):
    u = pd.read_csv(R / "us_by_decade.csv")
    ax.plot(u["decade"], u["based_us_pct"], color=ORANGE, marker="o", linewidth=2.5, label="worked in the US (science prizes)")
    ax.plot(u["decade"], u["born_us_pct"], color=BLUE, marker="o", linewidth=2.5, label="born in the US (all prizes to people)")
    ax.set_xticks(u["decade"]); ax.set_xticklabels([LABEL(d) for d in u["decade"]], fontsize=9 if not big else 10)
    ax.set_ylim(0, 80); ax.set_ylabel("% of laureates"); ax.grid(axis="x", visible=False)
    peak = u.loc[u["based_us_pct"].idxmax()]
    ax.annotate(f"{peak['based_us_pct']:.0f}% of 1990s science laureates\nworked in the US; {peak['foreign_born_pct_of_us_based']:.0f}% of them\nwere born elsewhere", (peak["decade"], peak["based_us_pct"]),
                (1938, 66), color=INK, fontsize=10, arrowprops={"arrowstyle": "-", "color": DIM})
    ax.legend(frameon=False, labelcolor=INK, fontsize=9, loc="lower right", bbox_to_anchor=(1, 0.0))
    ax.set_title("Where the laureates were born, and where they worked")


def team(ax):
    t = pd.read_csv(R / "team_size.csv"); x = np.arange(len(t)); bottom = np.zeros(len(t))
    for col, color, name in [("alone", BLUE, "one laureate"), ("two", GRAY, "shared by two"), ("three", ORANGE, "shared by three")]:
        v = 100 * t[col] / t["prizes"]
        ax.bar(x, v, bottom=bottom, color=color, width=0.72, label=name); bottom += v
    ax.set_xticks(x); ax.set_xticklabels([LABEL(d) for d in t["decade"]], fontsize=9); ax.set_ylim(0, 100)
    ax.set_ylabel("% of science prizes"); ax.grid(axis="x", visible=False)
    ax.set_title("Physics, chemistry and medicine prizes: the lone laureate fades")
    ax.legend(frameon=False, labelcolor=INK, fontsize=9, loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.12))


def main():
    (HERE / "charts").mkdir(exist_ok=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={"width_ratios": [1.15, 1]})
    us(a, big=True); team(b)
    for ax in (a, b):
        ax.title.set_fontsize(15)
    fig.suptitle("Who wins the Nobel Prize? 1,026 prizes, 1901 to 2025", x=0.01, ha="left", fontsize=20, color=INK, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(HERE / "charts" / "00_cover.png", dpi=100); plt.close(fig)

    w = pd.read_csv(R / "women.csv"); dec = w.groupby("decade")[["laureates", "women"]].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.bar(dec["decade"], 100 * dec["women"] / dec["laureates"], width=7, color=ORANGE)
    for _, r in dec.iterrows():
        ax.text(r["decade"], 100 * r["women"] / r["laureates"] + 0.6, f"{int(r['women'])}/{int(r['laureates'])}", ha="center", color=INK, fontsize=9)
    ax.set_xticks(dec["decade"]); ax.set_xticklabels([LABEL(d) for d in dec["decade"]], fontsize=9)
    ax.set_ylabel("% of laureates who are women"); ax.grid(axis="x", visible=False)
    ax.set_title("Women among laureates, by decade (first: Marie Curie, physics, 1903)")
    save(fig, "01_women.png")

    fig, ax = plt.subplots(figsize=(10, 3.8)); us(ax); save(fig, "02_us.png")

    age = pd.read_csv(R / "age.csv"); fig, ax = plt.subplots(figsize=(10, 3.8))
    for cat, color, ls in [("Physics", ORANGE, "-"), ("Chemistry", BLUE, "-"), ("Physiology or Medicine", GREEN, "-"), ("Literature", GRAY, "-"), ("Peace", GRAY, (0, (3, 2)))]:
        ax.plot(age["decade"], age[cat], color=color, marker="o", linewidth=2, linestyle=ls, label=cat)
    ax.set_xticks(age["decade"]); ax.set_xticklabels([LABEL(d) for d in age["decade"]], fontsize=9); ax.set_ylim(40, 80)
    ax.set_ylabel("median age when awarded"); ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, labelcolor=INK, fontsize=9, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.set_title("Older with each generation: median age of physics laureates, 42 in the 1930s, 77 in 2020-25")
    save(fig, "03_age.png")

    fig, ax = plt.subplots(figsize=(10, 3.8)); team(ax); save(fig, "04_team.png")


if __name__ == "__main__":
    main()
