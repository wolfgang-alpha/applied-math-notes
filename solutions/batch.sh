#!/usr/bin/env bash
# Compile the solution sheets: every lectureNN.tex in this folder becomes lectureNN.pdf.
#   ./batch.sh
# Needs pdflatex and latexmk (TeX Live). The FEniCS scripts lectureNN_exerciseK.py are only included as listings;
# they are not run here (see the README for running FEniCS).
set -euo pipefail
cd "$(dirname "$0")"

for tex in lecture[0-9][0-9].tex; do
    latexmk -pdf -interaction=nonstopmode -halt-on-error -quiet "$tex"
done
latexmk -c -quiet lecture[0-9][0-9].tex    # remove the auxiliary files, keep the PDFs
