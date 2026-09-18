"""
Digitise a Huang et al. (2015) stacked count-histogram figure into a CSV.

Finds the panel frames and spines, calibrates the wavelength axis from the
major tick marks, then measures each bar as a contiguous run of dark pixels
rising from its panel baseline. Bar heights are recovered as counts purely so
the per-panel sum can be checked against the N printed on the panel.

Usage
-----
    python digitize_panels.py <image> <y_axis_max> <Scale1,Scale2,...> <out.csv>

Example
-------
    python digitize_panels.py fig.png 15 Leaves,Canopies,Landscape \
        huang2015_chlorophylla.csv

List only the scales that actually have a panel, in top-to-bottom order; a
scale with no panel is simply absent from the CSV and plots as an empty row.
"""
import sys, csv
import numpy as np
from PIL import Image


def frames(dark, min_frac=0.55):
    """Horizontal frame lines (panel tops/bottoms) and the two vertical spines."""
    h, w = dark.shape
    rows = dark.sum(axis=1)
    hits = [y for y in range(h) if rows[y] > min_frac * w * 0.62]
    groups = []
    for y in hits:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    ys = [int(np.mean(g)) for g in groups]
    cols = dark.sum(axis=0)
    vhits = [x for x in range(w) if cols[x] > 0.55 * h * 0.5]
    vgroups = []
    for x in vhits:
        if vgroups and x - vgroups[-1][-1] <= 2:
            vgroups[-1].append(x)
        else:
            vgroups.append([x])
    xs = [int(np.mean(g)) for g in vgroups]
    return ys, xs


def major_ticks(dark, L, R, bot):
    """Major x ticks = the longer marks just below a panel's baseline."""
    lens = []
    for x in range(L, R + 1):
        n = 0
        for y in range(bot + 2, bot + 18):
            if dark[y, x]:
                n += 1
        lens.append(n)
    marks = [(x, lens[x - L]) for x in range(L, R + 1) if lens[x - L] >= 4]
    groups = []
    for x, n in marks:
        if groups and x - groups[-1][-1][0] <= 2:
            groups[-1].append((x, n))
        else:
            groups.append([(x, n)])
    longest = max(max(p[1] for p in g) for g in groups)
    out = []
    for g in groups:
        if max(p[1] for p in g) >= longest - 2:
            out.append(sum(p[0] for p in g) / len(g))
    return out


def main(path, ymax, labels, out_csv):
    im = Image.open(path).convert("L")
    a = np.array(im)
    dark = a < 128
    ys, xs = frames(dark)
    L, R = xs[0], xs[-1]
    print("image %s  frame rows %s  spines x=%d..%d" % (a.shape, ys, L, R))
    panels = [(ys[i], ys[i + 1]) for i in range(0, len(ys) - 1, 2)]
    assert len(panels) == len(labels), "found %d panels, expected %d" % (
        len(panels), len(labels))

    mt = major_ticks(dark, L, R, panels[0][1])
    print("major ticks found: %d -> %s ... %s" % (len(mt), mt[:3], mt[-2:]))
    w0, w1 = 350.0, 350.0 + 50.0 * (len(mt) - 1)
    x0, x1 = mt[0], mt[-1]
    nm = lambda x: w0 + (x - x0) * (w1 - w0) / (x1 - x0)
    print("x calibration: %.1f px -> %.0f nm ; %.1f px -> %.0f nm" % (x0, w0, x1, w1))
    mid = mt[len(mt) // 2]
    print("  check: middle tick %.1f px -> %.2f nm (expect %.0f)"
          % (mid, nm(mid), w0 + 50 * (len(mt) // 2)))

    rows = []
    for (top, bot), label in zip(panels, labels):
        ppu = (bot - top) / float(ymax)
        heights = {}
        for x in range(L + 2, R - 1):
            h, y = 0, bot - 1
            while y > top and dark[y, x]:
                h += 1
                y -= 1
            if h >= 0.35 * ppu:
                heights[x] = h
        groups = []
        for x in sorted(heights):
            if groups and x - groups[-1][-1] <= 1:
                groups[-1].append(x)
            else:
                groups.append([x])
        tot = 0
        bars = []
        for g in groups:
            cx = (g[0] + g[-1]) / 2.0
            cnt = max(heights[x] for x in g) / ppu
            bars.append((round(nm(cx), 1), round(cnt, 2), int(round(cnt))))
            tot += int(round(cnt))
        print("\n=== %s: %d bars, counts sum to %d" % (label, len(bars), tot))
        for wl, raw, c in bars:
            print("     %6.1f nm  raw=%5.2f -> %d" % (wl, raw, c))
            rows.append((label, wl, raw, c))

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scale", "wavelength_nm", "count_raw", "count"])
        w.writerows(rows)
    print("\nwrote", out_csv, "with", len(rows), "bars")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3].split(","), sys.argv[4])
