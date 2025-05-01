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
octahedron_vertices = np.array([
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
]) / np.sqrt(1)

edges = [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)]

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

arcs = []
principal_vector = [np.zeros(3) for _ in range(6)]

for u, v in edges:
    v0, v1 = octahedron_vertices[u], octahedron_vertices[v]
    arc = spherical_interpolation(v0, v1, num_points=30)
    arcs.append((u, v, arc))
    principal_vector[u] = arc[1] - arc[0]
    principal_vector[v] = arc[-1] - arc[-2]

for i, p in enumerate(principal_vector):
    p /= np.linalg.norm(p)
    principal_vector[i] = p

place_pegs_left = [(0, 4)]
place_pegs_right = [(0, 4)]

octahedron = Network(
    vertex_count=6,
    paths=arcs,
    pegs=[(arcs[i][:2] in place_pegs_left, arcs[i][:2] in place_pegs_right) for i in range(len(arcs))],
    start=(0, 0),
    coords=octahedron_vertices,
    principal_vector=np.array(principal_vector),
    normal_vector=octahedron_vertices,
    kind=4,
)
