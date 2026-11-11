# Minimum potential energy on a suspension bridge.
#
# The bridge of bridge_mesh.py under its own weight, as a problem of linear elasticity in 3D, solved as in
# chapter 3: write down the total potential energy, let derivative produce the variational formulation, solve.
# The script writes three pictures:
#
#   bridge_mesh.png             the mesh
#   bridge_energy_density.png   the bridge in equilibrium, coloured by the strain energy density
#   bridge_minimum_energy.gif   the displacement grows from zero to the equilibrium displacement,
#                               and the total potential energy falls to its minimum
#
#   python3 bridge.py        (in this folder; needs legacy FEniCS and matplotlib)
from fenics import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, PowerNorm, to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

set_log_level(LogLevel.WARNING)

# ---------------------------------------------------------------- the problem, as in chapter 3
mesh = Mesh('bridge.xml.gz')

E, nu = 1000.0, 0.3
rho_g = 0.3                  # own weight per unit volume
kappa = E/(3*(1 - 2*nu))     # bulk modulus
G     = E/(2*(1 + nu))       # shear modulus

V = VectorFunctionSpace(mesh, 'Lagrange', 1)

def epsilon(u):
    return sym(grad(u))

def psi(eps):                # strain energy density
    return 0.5*kappa*tr(eps)**2 + G*inner(dev(eps), dev(eps))

def fixed(x, on_boundary):   # the foot of the piers and of the abutments, and the outer faces of the abutments
    return on_boundary and (near(x[2], -2.2, 1e-6) or abs(x[0]) > 10.5 - 1e-6)

bc = DirichletBC(V, Constant((0.0, 0.0, 0.0)), fixed)
f  = Constant((0.0, 0.0, -rho_g))

u = Function(V)
v = TestFunction(V)

Pi  = (psi(epsilon(u)) - dot(f, u)) * dx
dPi = derivative(Pi, u, v)
solve(dPi == 0, u, bc, solver_parameters={'newton_solver': {'linear_solver': 'mumps'}})

print("%d nodes, %d tetrahedra, %d unknowns" % (mesh.num_vertices(), mesh.num_cells(), V.dim()))
print("deflection of the deck at midspan: %.4f" % u(0.0, 0.0, -0.15)[2])
print("Pi(u) = %.4f,  -Psi(u) = %.4f" % (assemble(Pi), -assemble(psi(epsilon(u))*dx)))

# ---------------------------------------------------------------- on the way to equilibrium
# The total potential energy of the displacement xi*u, under the full weight: xi = 0 is the undeformed
# bridge, xi = 1 the equilibrium. The values beyond xi = 1 are for the dotted line at the end of the film.
u_equilibrium = u.vector().copy()
xi_values = np.linspace(0.0, 1.3, 53)
Pi_values = np.zeros(len(xi_values))
for k, xi in enumerate(xi_values):
    u.vector().zero()
    u.vector().axpy(xi, u_equilibrium)
    Pi_values[k] = assemble(Pi)
u.vector().zero()
u.vector().axpy(1.0, u_equilibrium)
steps = int(np.sum(xi_values <= 1.0 + 1e-9))     # the steps up to xi = 1

# ---------------------------------------------------------------- the surface of the bridge, for the pictures
surface  = BoundaryMesh(mesh, 'exterior', False)       # triangles with outward normals
node     = surface.entity_map(0).array()               # node of the surface -> node of the mesh
triangle = surface.cells()
X = mesh.coordinates()[node]
U = u.compute_vertex_values(mesh).reshape(3, -1).T[node]

# strain energy density in equilibrium: smoothed to the nodes, then one value per triangle
density = project(psi(epsilon(u)), FunctionSpace(mesh, 'Lagrange', 1)).compute_vertex_values(mesh)
density = np.maximum(density[node][triangle].mean(axis=1), 0.0)
scale   = PowerNorm(0.5, vmin=0.0, vmax=np.percentile(density, 99))           # square-root colour scale
colours = ListedColormap(pyplot.get_cmap('OrRd')(np.linspace(0.12, 1.0, 256)))

elevation, azimuth = 11.0, -50.0                        # the view
a, e   = np.radians(azimuth), np.radians(elevation)
eye    = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])      # direction to the camera
across = np.array([-np.sin(a), np.cos(a), 0.0])                               # horizontal, across the view
ahead  = np.array([-np.cos(a), -np.sin(a), 0.0])                              # horizontal, away from the camera
light  = np.array([-0.35, -0.55, 0.75])/np.linalg.norm([-0.35, -0.55, 0.75])

def new_view(figure, shift=0.0, zoom=1.08):
    # a 3D view that fills the figure; the water ends in a horizon behind the bridge
    ax = figure.add_axes([0.0, -0.33 + shift, 1.0, 1.78], projection='3d', computed_zorder=False)
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_xlim(-10.5, 10.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-2.2, 3.35)
    ax.set_box_aspect((21.0, 3.0, 5.55), zoom=zoom)
    ax.set_axis_off()
    foot = np.array([0.0, 0.0, -2.2])
    water = [foot + s*60.0*across + t*ahead for s, t in ((-1, -40.0), (1, -40.0), (1, 10.0), (-1, 10.0))]
    ax.add_collection3d(Poly3DCollection([water], facecolors='#dde8ef', edgecolors='none', zorder=0))
    return ax

def draw_bridge(ax, xi, values=None, mesh_lines=False):
    # the surface displaced by xi*u; values: strain energy density per triangle, or None for a plain surface
    P = (X + xi*U)[triangle]
    normal = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    front = normal @ eye > -0.1                                  # leave out the faces that look away
    shade = 0.62 + 0.38*np.clip(normal @ light, 0.0, 1.0)
    if values is None:
        rgba = np.tile(to_rgba('#f3e7d8'), (len(P), 1))
    else:
        rgba = colours(scale(values))
    rgba[:, :3] *= shade[:, None]
    edges = '#1d243340' if mesh_lines else rgba[front]
    surface_3d = Poly3DCollection(P[front], facecolors=rgba[front], edgecolors=edges, linewidths=0.3, zorder=1)
    ax.add_collection3d(surface_3d)
    return surface_3d

def colour_bar(figure, position):
    cax = figure.add_axes(position)
    bar = figure.colorbar(ScalarMappable(norm=scale, cmap=colours), cax=cax, orientation='horizontal', extend='max')
    bar.set_label('strain energy density', fontsize=11)
    bar.outline.set_visible(False)

# ---------------------------------------------------------------- picture 1: the mesh
figure = pyplot.figure(figsize=(12.8, 7.2), dpi=150)       # 1920 x 1080 pixels
draw_bridge(new_view(figure), 0.0, mesh_lines=True)
figure.text(0.03, 0.93, "%d nodes, %d tetrahedra" % (mesh.num_vertices(), mesh.num_cells()), fontsize=13)
figure.savefig('bridge_mesh.png')
pyplot.close(figure)

# ---------------------------------------------------------------- picture 2: strain energy density in equilibrium
figure = pyplot.figure(figsize=(12.8, 7.2), dpi=150)       # 1920 x 1080 pixels
draw_bridge(new_view(figure), 1.0, density)
colour_bar(figure, [0.70, 0.085, 0.24, 0.022])
figure.text(0.03, 0.93, "Equilibrium under the own weight, true scale", fontsize=13)
figure.savefig('bridge_energy_density.png')
pyplot.close(figure)

# ---------------------------------------------------------------- film: from the undeformed state to equilibrium
figure = pyplot.figure(figsize=(9.6, 5.4), dpi=200)         # 1920 x 1080 pixels
ax = new_view(figure, shift=0.115, zoom=0.95)                # the bridge in the upper part of the frame
colour_bar(figure, [0.66, 0.185, 0.28, 0.024])

graph = figure.add_axes([0.085, 0.125, 0.44, 0.205])         # below it, the total potential energy on the way
graph.set_xlim(0.0, 1.3)
graph.set_ylim(1.12*Pi_values.min(), -0.12*Pi_values.min())
graph.set_xticks([0.0, 0.5, 1.0])
graph.set_yticks([0.0, -0.1, -0.2, -0.3])
graph.set_xlabel(r'$\xi$   (displacement $\xi\, u$)', fontsize=11)
graph.axhline(0.0, color='#c3c2b7', linewidth=1)
for side in ('top', 'right'):
    graph.spines[side].set_visible(False)
curve, = graph.plot([], [], color='#1d2433', linewidth=2.5)
point, = graph.plot([], [], 'o', color='#1d2433', markersize=7)

frames, bridge = [], None
for k in range(steps):
    xi = xi_values[k]
    if bridge is not None:
        bridge.remove()
    bridge = draw_bridge(ax, xi, xi**2*density)       # the strain energy density of xi*u is xi^2 times that of u
    curve.set_data(xi_values[:k + 1], Pi_values[:k + 1])
    point.set_data([xi], [Pi_values[k]])
    graph.set_title(r'total potential energy  $\Pi(\xi\, u)$ = %.3f  for  $\xi$ = %.2f' % (Pi_values[k], xi),
                    fontsize=11, loc='left')
    if k == steps - 1:                                # in equilibrium: beyond it the energy would rise again
        graph.plot(xi_values[k:], Pi_values[k:], ':', color='#1d2433', linewidth=1.5)
        graph.annotate('equilibrium: minimum of $\\Pi$', (1.0, Pi_values[k]), (0.42, 0.45*Pi_values.min()),
                       fontsize=10, arrowprops=dict(arrowstyle='-', color='#52514e'))
    figure.canvas.draw()
    frames.append(Image.frombuffer('RGBA', figure.canvas.get_width_height(), figure.canvas.buffer_rgba()).convert('RGB'))
pyplot.close(figure)

# GIF with one palette for all frames and without dithering, so that flat colours stay flat;
# 0.8 s on the undeformed bridge, then 70 ms per step, and 3 s in equilibrium
sample = Image.new('RGB', (3*frames[0].width, frames[0].height))
for k, frame in enumerate((frames[0], frames[steps//2], frames[-1])):
    sample.paste(frame, (k*frame.width, 0))
palette = sample.quantize(colors=256, method=2)       # method 2: fast octree
frames = [frame.quantize(palette=palette, dither=0) for frame in frames]
frames[0].save('bridge_minimum_energy.gif', save_all=True, append_images=frames[1:],
               duration=[800] + [70]*(steps - 2) + [3000], loop=0)
