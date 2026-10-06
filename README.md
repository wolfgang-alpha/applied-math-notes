# Applied math notes

Lecture notes on the finite element method with legacy [FEniCS](https://fenicsproject.org) (2019.1), as Jupyter
notebooks. Each lecture combines the theory with worked FEniCS examples and ends with exercises.

| Notebook | Topic |
|---|---|
| [lecture01.ipynb](lecture01.ipynb) | The Galerkin method |
| [lecture02.ipynb](lecture02.ipynb) | From the variational problem to the weak and the strong form |
| [lecture03.ipynb](lecture03.ipynb) | Strain and stress, a closer look |
| [lecture04.ipynb](lecture04.ipynb) | Time-dependent problems: the diffusion equation |
| [lecture05.ipynb](lecture05.ipynb) | Variational problems that are optimization problems: the hanging rope and shape optimization |

The notebooks are stored with their outputs, so they can be read on GitHub without running anything.

## Slides

[slides/lecture01.html](slides/lecture01.html) presents lecture 1 as [reveal.js](https://revealjs.com) slides. Clone or
download the repository and open the file in a browser. Everything it needs is in `slides/lib`, so it also works
offline. Arrow keys move through the slides, `S` opens the speaker view with notes and `F` switches to full screen. For
a PDF, add `?print-pdf` to the address and print the page.

`slides/lib` contains reveal.js (MIT license), MathJax (Apache License 2.0) and the fonts Source Sans 3 and JetBrains
Mono (SIL Open Font License 1.1), each with its license file.

## Running the notebooks with Docker

You need [Docker](https://docs.docker.com/get-docker/). The image runs on x86-64 and on ARM (Apple silicon). On
Windows, run the commands in a WSL terminal.

1. Build the image once. It is the FEniCS image of the
   [scientificcomputing](https://github.com/scientificcomputing/packages) project plus Jupyter:

   ```bash
   docker build -t fenics-notebook:2024-05-30 - <<'EOF'
   FROM ghcr.io/scientificcomputing/fenics-gmsh:2024-05-30
   RUN python3 -m pip install --no-cache-dir notebook
   EOF
   ```

2. Clone this repository and start Jupyter in it:

   ```bash
   git clone https://github.com/wolfgang-alpha/applied-math-notes.git
   cd applied-math-notes
   docker run --rm -it -p 8888:8888 \
       --user "$(id -u):$(id -g)" -e HOME=/tmp \
       -v "$PWD":/home/fenics/shared -w /home/fenics/shared \
       fenics-notebook:2024-05-30 \
       jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
   ```

3. Open the URL printed at the end (`http://127.0.0.1:8888/tree?token=...`) in a browser and click a notebook.
   Stop the server with Ctrl-C.

The container runs as your own user, so the plots and sound files the notebooks write belong to you, not root. If port
8888 is taken, use for example `-p 8899:8888` and replace 8888 by 8899 in the URL.
