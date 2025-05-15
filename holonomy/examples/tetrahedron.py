import numpy as np

from holonomy.curves import spherical_interpolation
from holonomy.graph import Network

__ALL__ = ["tetrahedron"]


R = 1
tetrahedron_vertices = np.array([
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, -1],
    [1, -1, -1],
]) / np.sqrt(3)

edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

arcs = []
principal_vector = [np.zeros(3) for _ in range(4)]

for u, v in edges:
    v0, v1 = tetrahedron_vertices[u], tetrahedron_vertices[v]
    arc = spherical_interpolation(v0, v1, num_points=30)
    arcs.append((u, v, arc))
    principal_vector[u] = arc[1] - arc[0]
    principal_vector[v] = arc[-1] - arc[-2]

for i, p in enumerate(principal_vector):
    p /= np.linalg.norm(p)
    principal_vector[i] = p

tetrahedron = Network(
    vertex_count=4,
    paths=arcs,
    pegs=[(False, False) for _ in range(len(arcs))],
    start=(0, 0),
    coords=tetrahedron_vertices,
    principal_vector=np.array(principal_vector),
    normal_vector=tetrahedron_vertices,
    kind=6,
)
