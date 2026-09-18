---
name: paper-note
description: Create or update a one-page LaTeX reading note for a scientific paper in this repo — scaffolding <key>.tex and <key>/, filling in the DOI and takeaways, adding figures, and building the PDF. Use whenever Prabu says he is reading, has read, or wants notes on a paper, names a DOI or paper title to record, or asks to add a figure or takeaway to an existing note.
---

# Paper reading notes

One note per paper, one page where possible. The note is a reminder of why the
paper mattered — not a summary.

## Layout

Everything paper-related lives in `papernotes/` (set 2026-09-18). The repo root
is for topic notes only — `community_weighting`, `integrating_sphere`,
`spectroXmeter` — which have their own preambles and are not paper notes.

```
papernotes/<key>.tex        the note
papernotes/<key>/           every figure for that note, nothing else
papernotes/papernote.sty    shared preamble
papernotes/_template.tex    skeleton to copy
```

`<key>` is `firstauthorYEAR_topic`, lowercase, e.g. `huang2015_pigments`,
`smith2023_canopy`. The `.tex` and the directory always share it, and
`\graphicspath{{<key>/}}` connects them.

Figure files are named for what they show, prefixed by the key where it helps:
`huang2015_carotenoids.png`, `meta_analysis_R2.png`, `paper_title.png`.

## Creating a note

Scaffold it straight away — **do not look the paper up**. Prabu gives the key and
the DOI; he does not want the DOI resolved, the title fetched, or the abstract
read (said 2026-09-18). The takeaways are his to write, not ours to draft from an
abstract.

1. In `papernotes/`, copy `_template.tex` to `<key>.tex` and `mkdir <key>`.
   Replace `KEY` in the header comment and in `\graphicspath`.
2. Replace `KEY/` in `\graphicspath` with the real key.
3. Fill `\paperdoi{...}` with the bare DOI — no `https://doi.org/` prefix, the
   macro adds it.
4. Write the takeaways (see below).
5. `make papernotes/<key>.pdf` from the repo root, then show the note.

`papernote.sty` carries the shared preamble; never copy those packages into a
note. Anything genuinely specific to one note (a `\newlength` for panel sizing,
say) belongs in that note, not the package.

## The paper_title figure

Prabu calls this **the paper_title figure** (agreed 2026-09-18) — use that name,
not "the first figure" or "the title image", and say so if he reaches for
another name, since he asked to be reminded.

`\papertitle{paper_title.png}` opens the note with a screenshot of the paper's
title block. It is uncaptioned and outside the figure numbering on purpose, so
the first real figure is Figure 1.

**Papers often have no image to add.** Delete the `\papertitle` line and the
note is still correct — do not substitute a placeholder, and do not leave a
`\papertitle` pointing at a file that does not exist. A note with no figures at
all is fine: takeaways alone, no `\clearpage`.

## Takeaways

- The DOI is always the first bullet.
- Then a handful of bullets, each a claim worth remembering, in Prabu's words.
- A bullet that refers to a figure cites it as `Figure~\ref{fig:label}` so the
  reader can jump — the figures exist to support the bullets, not the reverse.
- Keep it to what earns its place. Two good bullets beat eight dutiful ones.

## Adding a figure later

Put the file in `papernotes/<key>/`, add a `figure[H]` block with a caption and a
`\label{fig:...}`, and reference it from the relevant bullet. Use `\clearpage`
between figures that each want their own page.

## Building

`make papernotes/<key>.pdf` runs pdflatex twice so `\ref` resolves, from inside
`papernotes/` so `\graphicspath` and `papernote.sty` resolve; it then deletes
the `.aux`/`.log`/`.out` it produced. `make` alone rebuilds every note, paper or
topic, whose source is newer than its PDF. Expect font-substitution
warnings from the topic notes — cosmetic, not errors. PDFs are tracked in git
here, so a rebuild shows up as a change.

**Always end a change by building and showing the PDF — never the `.tex`.**
Prabu reads the rendered note, not the source (said 2026-09-18). Every edit,
however small, is followed by `make <key>.pdf` and then the PDF in the file
pane. Do not open the `.tex` in the pane, and do not paste LaTeX into the reply
unless he asks to see the markup.

Show the **PDF** in the file pane — never a PNG rendering of it (Prabu ruled
that out 2026-09-18). If the pane shows it blank, say so and leave it; do not
substitute page images.

The pane caches by path: point it at another file first, then at the PDF.
