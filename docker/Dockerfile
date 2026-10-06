# Image for the notebooks of https://github.com/wolfgang-alpha/applied-math-notes:
# legacy FEniCS 2019.1, Gmsh 4.12.2 with OpenCASCADE, meshio and h5py (all from the base image) plus Jupyter Notebook.
#
# Build and push for x86-64 and ARM:
#   docker buildx build --platform linux/amd64,linux/arm64 \
#       -t wolfla/fenics-notebook:2026-10-06 -t wolfla/fenics-notebook:latest --push docker/
FROM ghcr.io/scientificcomputing/fenics-gmsh:2024-05-30

RUN python3 -m pip install --no-cache-dir notebook==7.6.3

# Works with docker run --user "$(id -u):$(id -g)": any user gets a writable home.
# --allow-root covers runs without --user (e.g. Docker Desktop on macOS).
ENV HOME=/tmp
WORKDIR /home/fenics/shared
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
