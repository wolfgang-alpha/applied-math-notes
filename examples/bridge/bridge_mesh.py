# A tetrahedral mesh of a suspension bridge in the style of the Golden Gate Bridge.
#
# The geometry is put together from simple solids with Gmsh (OpenCASCADE kernel): deck, two towers with
# piers and struts, two abutments, two main cables and the hangers. All parts are fused into one body and
# meshed; the result is written as bridge.xml.gz, which FEniCS reads with Mesh('bridge.xml.gz').
#
#   python3 bridge_mesh.py        (needs gmsh and meshio, both are in the Docker image of the notes)
import gzip
import os
import shutil

import gmsh
import meshio
import numpy as np

# dimensions; x runs along the bridge, y across, z up, and the road surface is z = 0
span, side = 12.0, 4.0                 # main span between the towers, length of a side span
x_tower, x_end = span/2, span/2 + side
half_width, deck_thickness = 1.0, 0.3  # deck
z_water = -2.2                         # foot of the piers and of the abutments
z_saddle, z_sag, z_anchor = 3.2, 0.5, -0.1   # height of the cables: on the towers, at midspan, at the anchorage
y_cable = 0.9                          # the two cables and the hangers lie in the planes y = +-y_cable


def cable(x):
    # height of the centre line of a cable: a parabola in the main span, a slightly sagging line in the side spans
    if abs(x) <= x_tower:
        return z_sag + (z_saddle - z_sag)*(x/x_tower)**2
    s = (abs(x) - x_tower)/side
    return z_saddle + (z_anchor - z_saddle)*s - s*(1 - s)


gmsh.initialize()
gmsh.option.setNumber('General.Terminal', 0)
occ = gmsh.model.occ


def box(x0, x1, y0, y1, z0, z1):
    return (3, occ.addBox(x0, y0, z0, x1 - x0, y1 - y0, z1 - z0))


def cable_band(sign):
    # the cable as a band of height t in the plane y = const, extruded by the width w
    t, w = 0.18, 0.16
    y0 = sign*y_cable - w/2
    spans = [np.linspace(-x_end, -x_tower, 9), np.linspace(-x_tower, x_tower, 25), np.linspace(x_tower, x_end, 9)]
    tags = {}

    def point(x, z):
        key = (round(x, 9), round(z, 9))
        if key not in tags:
            tags[key] = occ.addPoint(x, y0, z)
        return tags[key]

    curves = [occ.addSpline([point(x, cable(x) - t/2) for x in xs]) for xs in spans]                # lower edge
    curves.append(occ.addLine(point(x_end, cable(x_end) - t/2), point(x_end, cable(x_end) + t/2)))
    curves += [occ.addSpline([point(x, cable(x) + t/2) for x in xs[::-1]]) for xs in spans[::-1]]   # upper edge, back
    curves.append(occ.addLine(point(-x_end, cable(-x_end) + t/2), point(-x_end, cable(-x_end) - t/2)))
    surface = occ.addPlaneSurface([occ.addCurveLoop(curves)])
    return [entity for entity in occ.extrude([(2, surface)], 0, w, 0) if entity[0] == 3][0]


parts = [box(-x_end, x_end, -half_width, half_width, -deck_thickness, 0.0)]            # deck

for xt in (-x_tower, x_tower):                                                         # towers
    parts.append(box(xt - 0.6, xt + 0.6, -1.45, 1.45, z_water, z_water + 0.4))         # pier
    for sign in (-1, 1):                                                               # legs, stepped
        for z0, z1, w in ((z_water + 0.4, 0.95, 0.50), (0.95, 2.5, 0.44), (2.5, 3.35, 0.38)):
            parts.append(box(xt - w/2 - 0.03, xt + w/2 + 0.03, sign*y_cable - w/2, sign*y_cable + w/2, z0, z1))
    for z0, z1 in ((-0.8, -0.45), (0.95, 1.2), (1.8, 2.03), (2.5, 2.7), (3.07, 3.35)):  # struts between the legs
        parts.append(box(xt - 0.2, xt + 0.2, -y_cable, y_cable, z0, z1))

for sign in (-1, 1):
    parts.append(box(sign*x_end - 0.5, sign*x_end + 0.5, -1.5, 1.5, z_water, 0.0))      # abutment
    parts.append(cable_band(sign))                                                     # main cable
    hangers = list(np.arange(-5.25, 5.26, 0.75)) + [-9.0, -8.25, -7.5, -6.75, 6.75, 7.5, 8.25, 9.0]
    for x in hangers:
        parts.append(box(x - 0.04, x + 0.04, sign*y_cable - 0.04, sign*y_cable + 0.04, -0.05, cable(x)))

body, _ = occ.fuse(parts[:1], parts[1:])
occ.synchronize()
assert len(body) == 1, 'the parts do not form one body'
gmsh.model.addPhysicalGroup(3, [body[0][1]])

# element size: 0.3 in general, 0.1 at the cables and the hangers
gmsh.option.setNumber('Mesh.MeshSizeMin', 0.05)
gmsh.option.setNumber('Mesh.MeshSizeMax', 0.3)
for sign in (-1, 1):
    points = gmsh.model.getEntitiesInBoundingBox(-x_end - 1, sign*y_cable - 0.1, 0.02, x_end + 1, sign*y_cable + 0.1, 4.0, 0)
    gmsh.model.mesh.setSize(points, 0.1)
gmsh.model.mesh.generate(3)
gmsh.model.mesh.optimize('Netgen')

here = os.path.dirname(os.path.abspath(__file__))
msh, xml = os.path.join(here, 'bridge.msh'), os.path.join(here, 'bridge.xml')
gmsh.write(msh)
gmsh.finalize()

mesh = meshio.read(msh)
tetrahedra = mesh.get_cells_type('tetra')
meshio.write(xml, meshio.Mesh(points=mesh.points, cells=[('tetra', tetrahedra)]))
with open(xml, 'rb') as source, gzip.GzipFile(xml + '.gz', 'wb', mtime=0) as target:    # mtime=0: reproducible file
    shutil.copyfileobj(source, target)
os.remove(msh)
os.remove(xml)
print('bridge.xml.gz: %d nodes, %d tetrahedra' % (len(mesh.points), len(tetrahedra)))
