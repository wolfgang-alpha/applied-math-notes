# Lecture 1, exercise 1: -u'' = 1 on (0, 1), u(0) = 0, u'(1) = 0, exact solution u = x - x^2/2
from fenics import *

set_log_level(LogLevel.WARNING)

mesh = IntervalMesh(20, 0.0, 1.0)
u_exact = Expression('x[0] - 0.5*x[0]*x[0]', degree=6)

def left(x, on_boundary):
    return on_boundary and near(x[0], 0.0)

for degree in [1, 2, 3]:
    V  = FunctionSpace(mesh, 'Lagrange', degree)
    u  = TrialFunction(V)
    v  = TestFunction(V)
    uh = Function(V)
    solve(inner(grad(u), grad(v))*dx == Constant(1.0)*v*dx, uh, DirichletBC(V, Constant(0.0), left))

    nodes = mesh.coordinates()[:, 0]
    nodal = max(abs(uh(x) - u_exact(x)) for x in nodes)
    print('degree %d: max nodal error %.1e, L2 error %.3e' % (degree, nodal, errornorm(u_exact, uh, 'L2')))
