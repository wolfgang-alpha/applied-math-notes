#!/usr/bin/env bash
# Compile the solution sheets: every chapterNN.tex in this folder becomes chapterNN.pdf.
#   ./batch.sh
# Needs pdflatex and latexmk (TeX Live). The FEniCS scripts chapterNN_exerciseK.py are only included as listings;
# they are not run here (see the README for running FEniCS).
set -euo pipefail
cd "$(dirname "$0")"

for tex in chapter[0-9][0-9].tex; do
    latexmk -pdf -interaction=nonstopmode -halt-on-error -quiet "$tex"
done
latexmk -c -quiet chapter[0-9][0-9].tex    # remove the auxiliary files, keep the PDFs
