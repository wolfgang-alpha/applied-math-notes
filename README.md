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

Lecture 1: [PDF](slides/lecture01.pdf) to read on GitHub, [HTML](slides/lecture01.html) to present (works offline
after cloning; `slides/lib` bundles reveal.js, MathJax and the fonts with their licenses).

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
