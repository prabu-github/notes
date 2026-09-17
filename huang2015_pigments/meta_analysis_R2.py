"""
Weighted meta-analysis R-squared by pigment and observation scale.

Reformat of the grouped bar chart in Huang et al. (2015): pastel fills in
place of the hatch/dot patterns, n-labels dropped from above the error bars
(they stay in meta_analysis_R2.csv), and the y axis named for what it is.

Anthocyanin has no canopy-scale estimate, so that slot is simply left empty -
the bar positions stay on the same grid as every other group.

Usage
-----
    python meta_analysis_R2.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator

HERE = Path(__file__).parent
DATA = HERE / "meta_analysis_R2.csv"
STEM = "meta_analysis_R2"
TITLE = "Meta-analysis $R^2$ for pigments (Huang et al. 2015)"

PIGMENTS = ["Chl tot", "Chl a", "Chl b", "Cars", "Anth"]
SCALES = ["Leaves", "Canopies", "Landscape"]

# Pastel fill with a deeper edge of the same hue, so each bar keeps a crisp
# outline at small sizes. Position within the group is the primary cue for
# which scale a bar belongs to; colour reinforces it.
FILL = {"Leaves": "#A6C4E8", "Canopies": "#F6C391", "Landscape": "#C4AEDB"}
EDGE = {"Leaves": "#4A7AB0", "Canopies": "#C07F35", "Landscape": "#7B5EA7"}

INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#d8d7d2"
SURFACE = "#ffffff"

BAR_W = 0.24
PITCH = 0.265                       # centre spacing: leaves a gap between fills
OFFSET = {"Leaves": -PITCH, "Canopies": 0.0, "Landscape": PITCH}


def load(path):
    out = {}
    with open(path) as fh:
        for row in csv.DictReader(fh):
            out[(row["pigment"], row["scale"])] = (
                float(row["r2"]), float(row["err_low"]), float(row["err_high"]))
    return out


def main():
    data = load(DATA)

    fig, ax = plt.subplots(figsize=(7.4, 4.15))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for i, pig in enumerate(PIGMENTS):
        for scale in SCALES:
            rec = data.get((pig, scale))
            if rec is None:
                continue                      # no estimate at this scale
            r2, lo, hi = rec
            x = i + OFFSET[scale]
            ax.bar(x, r2, width=BAR_W, color=FILL[scale],
                   edgecolor=EDGE[scale], linewidth=0.8, zorder=2)
            ax.errorbar(x, r2, yerr=[[lo], [hi]], fmt="none", ecolor=INK_SOFT,
                        elinewidth=0.9, capsize=2.5, capthick=0.9, zorder=3)

    ax.set_title(TITLE, fontsize=13, color=INK, loc="center", pad=36)
    ax.set_ylabel("Weighted meta-analysis $R^2$", fontsize=10.5, color=INK,
                  labelpad=8)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.set_xticks(range(len(PIGMENTS)))
    ax.set_xticklabels(PIGMENTS, fontsize=10, color=INK)
    ax.set_xlim(-0.6, len(PIGMENTS) - 0.4)
    # Uniform horizontal grid every 0.1; labels stay at every 0.2.
    ax.grid(axis="y", which="both", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", which="major", labelsize=9, colors=INK_SOFT,
                   length=4, width=0.7)
    ax.tick_params(axis="y", which="minor", length=2, width=0.5, colors=GRID)
    ax.tick_params(axis="x", length=0, pad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_SOFT)
        ax.spines[side].set_linewidth(0.7)

    handles = [Patch(facecolor=FILL[s], edgecolor=EDGE[s], linewidth=0.8,
                     label=s) for s in SCALES]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.01),
              ncol=3, frameon=False, fontsize=9.5, labelcolor=INK,
              handlelength=1.3, handleheight=1.1, borderpad=0,
              columnspacing=1.8, handletextpad=0.6)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(HERE / f"{STEM}.{ext}", dpi=300, facecolor=SURFACE)
    print(f"wrote {STEM}.png and .pdf")
    for pig in PIGMENTS:
        got = [s for s in SCALES if (pig, s) in data]
        print(f"    {pig:<8s} {len(got)} scales: {', '.join(got)}")


if __name__ == "__main__":
    main()
