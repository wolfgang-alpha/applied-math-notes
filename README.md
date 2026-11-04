# Applied math notes

Lecture notes on the finite element method with legacy [FEniCS](https://fenicsproject.org) (2019.1), as Jupyter
notebooks. Each chapter combines the theory with worked FEniCS examples and ends with exercises.

| Notebook | Topic |
|---|---|
| [chapter01.ipynb](chapter01.ipynb) | The Galerkin method |
| [chapter02.ipynb](chapter02.ipynb) | The finite element method: local basis functions, sparse matrices and the conjugate gradient method |
| [chapter03.ipynb](chapter03.ipynb) | From the variational problem to the weak and the strong form |
| [chapter04.ipynb](chapter04.ipynb) | Strain and stress, a closer look |
| [chapter05.ipynb](chapter05.ipynb) | Time-dependent problems: the diffusion equation |
| [chapter06.ipynb](chapter06.ipynb) | Variational problems that are optimization problems: the hanging rope and shape optimization |

The notebooks are stored with their outputs, so they can be read on GitHub without running anything.

## Slides

| Chapter | Slides |
|---|---|
| 1. The Galerkin method | [PDF](slides/chapter01.pdf), [HTML](slides/chapter01.html) |
| 2. The finite element method | [PDF](slides/chapter02.pdf), [HTML](slides/chapter02.html) |
| 3. Minimum potential energy | [PDF](slides/chapter03.pdf), [HTML](slides/chapter03.html) |

The PDFs can be read on GitHub; the HTML decks are for presenting (they work offline after cloning; `slides/lib`
bundles reveal.js, MathJax and the fonts with their licenses).

## Solutions

Solutions to the exercises on the slides: [chapter 1](solutions/chapter01.pdf), [chapter 2](solutions/chapter02.pdf),
[chapter 3](solutions/chapter03.pdf) (exercise 2).
The LaTeX sources are in [solutions](solutions); `solutions/batch.sh` compiles them (needs `pdflatex` and `latexmk`).
The FEniCS scripts there produce the numbers in the solutions.

## Running the notebooks with Docker

You need [Docker](https://docs.docker.com/get-docker/). The image
[wolfla/fenics-notebook](https://hub.docker.com/r/wolfla/fenics-notebook) contains legacy FEniCS 2019, Gmsh 4.12 with
OpenCASCADE, meshio and Jupyter, for x86-64 and ARM (Apple silicon); [docker/Dockerfile](docker/Dockerfile) shows how
it is built. On Windows, run the commands in a WSL terminal.

```bash
git clone https://github.com/wolfgang-alpha/applied-math-notes.git
cd applied-math-notes
docker run --rm -it -p 8888:8888 --user "$(id -u):$(id -g)" -v "$PWD":/home/fenics/shared wolfla/fenics-notebook:2026-10-06
```

The first start downloads the image (about 1.2 GB). Then open the URL printed at the end (`http://127.0.0.1:8888/tree?token=...`)
in a browser and click a notebook; stop the server with Ctrl-C. `--user` makes the plots and sound files the notebooks
write belong to you, not root. If port 8888 is taken, use for example `-p 8899:8888` and replace 8888 by 8899 in the
URL.

## Running the notebooks on Debian or Ubuntu, without Docker

On Debian 13 (trixie), Ubuntu 24.04 and newer, legacy FEniCS is in the standard repositories, so you need no Docker.
This also works in the Ubuntu app for WSL on Windows.

```bash
sudo apt install python3-dolfin jupyter-notebook python3-matplotlib python3-scipy git
git clone https://github.com/wolfgang-alpha/applied-math-notes.git
cd applied-math-notes
jupyter notebook
```

A browser opens with the notebook list (in WSL, open the printed URL yourself); click a notebook, and stop the server
with Ctrl-C in the terminal. The repositories ship legacy FEniCS 2019.2, a later snapshot than the 2019.1 in the Docker
image; all notebooks run unchanged with it. The package `fenics` installs the same plus the documentation and the C++
headers, which the notebooks don't need.
