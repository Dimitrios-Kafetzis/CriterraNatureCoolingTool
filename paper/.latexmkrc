# latexmk configuration for the methodology paper.
$pdf_mode  = 1;          # pdflatex
$bibtex_use = 2;         # run the bibliography tool and clean its output
$clean_ext = 'bbl run.xml synctex.gz nav snm vrb';
$out_dir   = '.';
# biblatex/biber dependency so latexmk reruns correctly
add_cus_dep('glo', 'gls', 0, 'makeglo');
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
