# Build the notes. `make` rebuilds only what changed.
#   topic notes  live at the repo root
#   paper notes  live in papernotes/, alongside papernote.sty

TOPIC_TEX := $(wildcard *.tex)
PAPER_TEX := $(filter-out papernotes/_template.tex,$(wildcard papernotes/*.tex))
PDFS      := $(TOPIC_TEX:.tex=.pdf) $(PAPER_TEX:.tex=.pdf)

LATEX := pdflatex -interaction=nonstopmode -halt-on-error

all: $(PDFS)

# Twice, so \ref cross-references resolve, then bin the scratch files:
# only the .tex and the .pdf are kept.
%.pdf: %.tex
	$(LATEX) $<
	$(LATEX) $<
	@rm -f $*.aux $*.log $*.out

# Paper notes build from inside papernotes/, so \graphicspath{{<key>/}} and
# \usepackage{papernote} both resolve relative to that directory.
papernotes/%.pdf: papernotes/%.tex papernotes/papernote.sty
	cd papernotes && $(LATEX) $*.tex && $(LATEX) $*.tex
	@rm -f papernotes/$*.aux papernotes/$*.log papernotes/$*.out

clean:
	rm -f *.aux *.log *.out papernotes/*.aux papernotes/*.log papernotes/*.out

.PHONY: all clean
