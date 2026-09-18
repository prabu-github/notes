# Build every paper/topic note. `make` rebuilds only what changed.

TEX  := $(filter-out _template.tex,$(wildcard *.tex))
PDFS := $(TEX:.tex=.pdf)

LATEX := pdflatex -interaction=nonstopmode -halt-on-error

all: $(PDFS)

# Twice, so \ref cross-references resolve, then bin the scratch files:
# only the .tex and the .pdf are kept.
%.pdf: %.tex papernote.sty
	$(LATEX) $<
	$(LATEX) $<
	@rm -f $*.aux $*.log $*.out

clean:
	rm -f *.aux *.log *.out

.PHONY: all clean
