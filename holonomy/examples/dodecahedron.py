import numpy as np

from holonomy.graph import Network


def spherical_interpolation(v0, v1, num_points=30):
    arc_points = []
    for t in np.linspace(0, 1, num_points):
        p = (1 - t) * v0 + t * v1
        p /= np.linalg.norm(p)
        arc_points.append(p)
    return np.array(arc_points)


R = 1
# g_r = golden ratio
g_r = (1 + np.sqrt(5)) / 2
dodecahedron_vertices = np.array([
    [-1, -1, -1],
    [-1, -1, 1],
    [-1, 1, -1],
    [-1, 1, 1],
    [1, -1, -1],
    [1, -1, 1],
    [1, 1, -1],
    [1, 1, 1],
    [0, -g_r, -1 / g_r],
    [0, -g_r, 1 / g_r],
    [0, g_r, -1 / g_r],
    [0, g_r, 1 / g_r],
    [-g_r, -1 / g_r, 0],
    [-g_r, 1 / g_r, 0],
    [g_r, -1 / g_r, 0],
    [g_r, 1 / g_r, 0],
    [-1 / g_r, 0, -g_r],
    [-1 / g_r, 0, g_r],
    [1 / g_r, 0, -g_r],
    [1 / g_r, 0, g_r],
]) / np.sqrt(3)

edges = [
    (0, 8),
    (0, 12),
    (0, 16),
    (1, 9),
    (1, 12),
    (1, 17),
    (2, 10),
    (2, 13),
    (2, 16),
    (3, 11),
    (3, 13),
    (3, 17),
    (4, 8),
    (4, 14),
    (4, 18),
    (5, 9),
    (5, 14),
    (5, 19),
    (6, 10),
    (6, 15),
    (6, 18),
    (7, 11),
    (7, 15),
    (7, 19),
    (8, 9),
    (10, 11),
    (12, 13),
    (14, 15),
    (16, 18),
    (17, 19),
]

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

arcs = []
principal_vector = [np.zeros(3) for _ in range(20)]

for u, v in edges:
    v0, v1 = dodecahedron_vertices[u], dodecahedron_vertices[v]
    arc = spherical_interpolation(v0, v1, num_points=30)
    arcs.append((u, v, arc))
    principal_vector[u] = arc[1] - arc[0]
    principal_vector[v] = arc[-1] - arc[-2]

for i, p in enumerate(principal_vector):
    p /= np.linalg.norm(p)
    principal_vector[i] = p

dodecahedron = Network(
    vertex_count=20,
    paths=arcs,
    pegs=[(False, False) for _ in range(len(arcs))],
    start=(0, 0),
    coords=dodecahedron_vertices,
    principal_vector=np.array(principal_vector),
    normal_vector=dodecahedron_vertices,
    kind=6,
)
