"""
Wavelength presence figures for the Huang et al. (2015) pigment compilation.

Each source figure is a stack of count histograms - one panel per observation
scale - showing which wavelengths published studies use for a given pigment.
This redraws them as a single presence matrix:

    x = wavelength, y = observation scale, dot = that wavelength is used.

Bar heights are deliberately discarded: the question is which bands are used,
not how often. Dots carry their true spectral colour, and the strip beneath
the rows doubles as the legend.

Per-trait inputs are ``<stem>.csv`` files produced by digitize_panels.py.
Register a trait in TRAITS below and it builds with everything else.

Usage
-----
    python wavelength_dots.py                      # rebuild every trait
    python wavelength_dots.py huang2015_chlorophylla   # rebuild just one
"""
import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

HERE = Path(__file__).parent

# --------------------------------------------------------------------------
# Traits. `n_reported` is the N printed on each source panel, used only to
# check the digitisation; None means that scale had no panel in the source.
# --------------------------------------------------------------------------
TRAITS = {
    "huang2015_chlorophylls": {
        "title": "Total chlorophyll (Huang et al. 2015)",
        "n_reported": {"Leaves": 131, "Canopies": 55, "Landscape": 46},
    },
    "huang2015_chlorophylla": {
        "title": "Chlorophyll $a$ (Huang et al. 2015)",
        "n_reported": {"Leaves": 53, "Canopies": 6, "Landscape": 6},
    },
    "huang2015_chlorophyllb": {
        "title": "Chlorophyll $b$ (Huang et al. 2015)",
        "n_reported": {"Leaves": 24, "Canopies": None, "Landscape": 2},
    },
    "huang2015_carotenoids": {
        "title": "Carotenoids (Huang et al. 2015)",
        "n_reported": {"Leaves": 40, "Canopies": 7, "Landscape": 4},
    },
    "huang2015_anthocyanin": {
        "title": "Anthocyanin (Huang et al. 2015)",
        "n_reported": {"Leaves": 43, "Canopies": None, "Landscape": 2},
    },
}

# Row order, top to bottom. Every figure keeps all three rows in the same
# position - a scale with no data keeps its label and an empty row - so
# figures for different traits can be stacked and read against each other.
SCALES = ["Leaves", "Canopies", "Landscape"]

INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#d8d7d2"
SURFACE = "#ffffff"
NIR_END = np.array([0.24, 0.24, 0.26])   # neutral the NIR ramp fades into
UV_END = np.array([0.30, 0.29, 0.33])    # neutral the UV ramp fades out of

XMIN, XMAX = 400, 950
VIS_MIN, VIS_MAX = 400.0, 700.0          # outside this, fade to neutral


def wavelength_to_rgb(w):
    """Approximate sRGB for a visible wavelength (Bruton), neutral outside it.

    Colour is only meaningful where the eye responds, so beyond VIS_MAX and
    below VIS_MIN the ramp fades to a dark neutral rather than inventing a
    hue for light nobody can see.
    """
    w = float(w)
    if w < 380:
        r, g, b = 0.35, 0.0, 0.45
    elif w < 440:
        r, g, b = -(w - 440) / 60.0, 0.0, 1.0
    elif w < 490:
        r, g, b = 0.0, (w - 440) / 50.0, 1.0
    elif w < 510:
        r, g, b = 0.0, 1.0, -(w - 510) / 20.0
    elif w < 580:
        r, g, b = (w - 510) / 70.0, 1.0, 0.0
    elif w < 645:
        r, g, b = 1.0, -(w - 645) / 65.0, 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0

    if w < 420:
        f = 0.55 + 0.45 * (w - 380) / 40.0
    elif w > 645:
        # Deep red darkens towards the edge of vision.
        f = 1.0 - 0.25 * min((w - 645) / 55.0, 1.0)
    else:
        f = 1.0
    rgb = np.clip(np.array([r, g, b]) * f, 0, 1) ** 0.8

    if w > VIS_MAX:
        t = min((w - VIS_MAX) / (XMAX - VIS_MAX), 1.0)
        rgb = (1 - t) * rgb + t * NIR_END
    elif w < VIS_MIN and VIS_MIN > XMIN:
        t = min((VIS_MIN - w) / (VIS_MIN - XMIN), 1.0)
        rgb = (1 - t) * rgb + t * UV_END

    # Keep every hue dark enough to read as a mark on white.
    lum = float(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])
    if lum > 0.62:
        rgb = rgb * (0.62 / lum)
    return tuple(np.clip(rgb, 0, 1))


def load_bands(path):
    """Return {scale: sorted distinct wavelengths} and {scale: summed count}."""
    bands = {s: set() for s in SCALES}
    totals = {s: 0 for s in SCALES}
    with open(path) as fh:
        for row in csv.DictReader(fh):
            scale = row["scale"]
            if scale not in bands:
                raise ValueError(f"{path.name}: unknown scale {scale!r}")
            bands[scale].add(round(float(row["wavelength_nm"]) / 5.0) * 5)
            totals[scale] += int(row["count"])
    return {s: sorted(v) for s, v in bands.items()}, totals


def plot_presence(bands, title, out_stem):
    fig = plt.figure(figsize=(7.2, 2.85))
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 0.085], hspace=0.16,
                          left=0.155, right=0.985, top=0.845, bottom=0.195)
    ax = fig.add_subplot(gs[0])
    axs = fig.add_subplot(gs[1], sharex=ax)
    for a in (ax, axs):
        a.set_facecolor(SURFACE)

    ax.set_title(title, fontsize=13, color=INK, loc="center", pad=12)

    for i, scale in enumerate(SCALES):
        y = len(SCALES) - i
        ax.axhline(y, color=GRID, lw=0.6, zorder=1)
        wls = bands[scale]
        if wls:
            face = [wavelength_to_rgb(w) for w in wls]
            edge = [tuple(np.array(c) * 0.55) for c in face]
            ax.scatter(wls, [y] * len(wls), s=46, c=face, edgecolors=edge,
                       linewidths=0.6, zorder=3, clip_on=False)
        ax.text(XMIN - 14, y, scale, ha="right", va="center",
                fontsize=9.5, color=INK)

    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(0.45, 3.55)
    ax.set_yticks([])
    ax.grid(axis="x", which="major", color=GRID, lw=0.5, zorder=0)
    ax.tick_params(axis="x", which="both", length=0, labelbottom=False)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    ramp = np.linspace(XMIN, XMAX, 1200)
    axs.imshow(np.array([[wavelength_to_rgb(w) for w in ramp]]),
               extent=[XMIN, XMAX, 0, 1], aspect="auto",
               interpolation="bilinear", zorder=2)
    axs.set_yticks([])
    axs.set_xlim(XMIN, XMAX)
    axs.xaxis.set_major_locator(MultipleLocator(50))
    axs.xaxis.set_minor_locator(MultipleLocator(10))
    axs.set_xlabel("Wavelength (nm)", fontsize=9.5, color=INK, labelpad=5)
    axs.tick_params(axis="x", which="major", labelsize=8.5, colors=INK_SOFT,
                    length=4, width=0.7)
    axs.tick_params(axis="x", which="minor", length=2, width=0.5, colors=GRID)
    for side in ("top", "right", "left"):
        axs.spines[side].set_visible(False)
    axs.spines["bottom"].set_color(INK_SOFT)
    axs.spines["bottom"].set_linewidth(0.7)
    axs.text(XMIN - 14, 0.5, "Spectrum", ha="right", va="center",
             fontsize=8, color=INK_SOFT)

    for ext in ("png", "pdf"):
        fig.savefig(out_stem.parent / f"{out_stem.name}.{ext}",
                    dpi=300, facecolor=SURFACE)
    plt.close(fig)


def build(stem):
    spec = TRAITS[stem]
    bands, totals = load_bands(HERE / f"{stem}.csv")
    plot_presence(bands, spec["title"], HERE / stem)
    print(f"{stem}.png/.pdf")
    for s in SCALES:
        n = spec["n_reported"].get(s)
        if n is None:
            note = "no panel in source"
        elif n == totals[s]:
            note = f"counts sum to {totals[s]} = N  OK"
        else:
            note = f"counts sum to {totals[s]} but panel says N={n}  CHECK"
        print(f"    {s:<10s} {len(bands[s]):>3d} bands   {note}")


def main(argv):
    stems = argv[1:] or list(TRAITS)
    unknown = [s for s in stems if s not in TRAITS]
    if unknown:
        raise SystemExit(f"unknown trait(s): {', '.join(unknown)}\n"
                         f"known: {', '.join(TRAITS)}")
    for stem in stems:
        build(stem)


if __name__ == "__main__":
    main(sys.argv)
