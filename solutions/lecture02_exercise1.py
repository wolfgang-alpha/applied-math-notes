# Lecture 2, exercise 1.2: CG iterations for the heated plate with different preconditioners (example 5)
from fenics import *

set_log_level(LogLevel.WARNING)

preconditioners = ['none', 'jacobi', 'ilu', 'amg']
print('   N        n' + ''.join('%9s' % p for p in preconditioners))
for N in [8, 16, 32, 64, 128, 256, 512]:
    mesh = RectangleMesh(Point(-1.0, -1.0), Point(1.0, 1.0), N, N)
    V    = FunctionSpace(mesh, 'Lagrange', 1)
    u, v = TrialFunction(V), TestFunction(V)
    bc   = DirichletBC(V, Constant(0.0), 'on_boundary')
    K, F = assemble_system(inner(grad(u), grad(v))*dx, Constant(1.0)*v*dx, bc)

    iterations = []
    for preconditioner in preconditioners:
        uh = Function(V)
        solver = KrylovSolver(K, 'cg', preconditioner)
        solver.parameters['relative_tolerance'] = 1e-10
        iterations.append(solver.solve(uh.vector(), F))
    print('%4d  %7d' % (N, V.dim()) + ''.join('%9d' % k for k in iterations))

# the diagonal of K: 4 at the interior nodes (h-independent), 1 in the Dirichlet rows set by assemble_system
mesh = RectangleMesh(Point(-1.0, -1.0), Point(1.0, 1.0), 16, 16)
V    = FunctionSpace(mesh, 'Lagrange', 1)
u, v = TrialFunction(V), TestFunction(V)
K, F = assemble_system(inner(grad(u), grad(v))*dx, Constant(1.0)*v*dx, DirichletBC(V, Constant(0.0), 'on_boundary'))
print('distinct diagonal entries of K (N = 16):', sorted(set(round(d, 12) for d in K.array().diagonal())))
