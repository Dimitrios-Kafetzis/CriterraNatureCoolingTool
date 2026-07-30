# Nature for Cooling methodology paper
#
#   make          build main.pdf
#   make watch    rebuild continuously on change
#   make clean    remove build artefacts, keep the PDF
#   make distclean remove build artefacts and the PDF

LATEXMK ?= latexmk
MAIN     = main

.PHONY: all watch clean distclean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib $(wildcard sections/*.tex) $(wildcard figures/*.tex)
	$(LATEXMK) -pdf $(MAIN).tex

watch:
	$(LATEXMK) -pdf -pvc $(MAIN).tex

clean:
	$(LATEXMK) -c $(MAIN).tex

distclean:
	$(LATEXMK) -C $(MAIN).tex
