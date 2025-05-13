import numpy as np

from holonomy.curves import cubic_bezier_connect
from holonomy.graph import Network

tetrahedron_vertices = np.array([
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, -1],
    [1, -1, -1],
])

tetrahedron_edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

vertices = []
for start, end in tetrahedron_edges:
    v_start = tetrahedron_vertices[start]
    v_end = tetrahedron_vertices[end]
    vertices.append((2 * v_start + v_end) / 3)
    vertices.append((v_start + 2 * v_end) / 3)
vertices = np.array(vertices)

edges = []
edge_length = np.linalg.norm(vertices[0] - vertices[1])
for i in range(len(vertices)):
    for j in range(i + 1, len(vertices)):
        if np.isclose(np.linalg.norm(vertices[i] - vertices[j]), edge_length):
            edges.append((i, j))

neighbors = [[] for _ in range(len(vertices))]
for i in range(len(vertices)):
    for j in range(len(vertices)):
        if i != j and np.isclose(np.linalg.norm(vertices[i] - vertices[j]), edge_length):
            neighbors[i].append(j)

sorted_neighbors = [[] for _ in range(len(vertices))]
for i in range(len(vertices)):
    vertex_neighbors = neighbors[i]
    if not vertex_neighbors:
        continue

    ref_vec = vertices[vertex_neighbors[0]] - vertices[i]
    ref_vec = ref_vec / np.linalg.norm(ref_vec)

    normal = vertices[i]

    x_axis = np.cross(normal, ref_vec)
    x_axis = x_axis / np.linalg.norm(x_axis)

    y_axis = np.cross(normal, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)

    angles = []
    for j in vertex_neighbors:
        proj_vec = vertices[j] - vertices[i]
        proj_vec = proj_vec - np.dot(proj_vec, normal) * normal
        proj_vec = proj_vec / np.linalg.norm(proj_vec)

        cos_angle = np.dot(x_axis, proj_vec)
        sin_angle = np.dot(y_axis, proj_vec)
        angle = np.arctan2(sin_angle, cos_angle)
        if angle < 0:
            angle += 2 * np.pi

        angles.append((j, angle))

    angles.sort(key=lambda x: x[1])
    sorted_neighbors[i] = [j for j, _ in angles]

vertices = vertices / np.linalg.norm(vertices, axis=1)[:, np.newaxis]

principal_vector = []
for i in range(len(vertices)):
    first_neighbor = sorted_neighbors[i][0]

    direction = vertices[first_neighbor] - vertices[i]

    normal_i = vertices[i].copy()
    radial_component = np.dot(direction, normal_i) * normal_i
    tangential_direction = direction - radial_component

    tangential_direction = tangential_direction / np.linalg.norm(tangential_direction)
    principal_vector.append(tangential_direction)

principal_vector = np.array(principal_vector)
truncated_tetrahedron = Network(
    vertex_count=len(vertices),
    paths=[],
    pegs=[],
    start=(0, 0),
    coords=vertices,
    principal_vector=principal_vector,
    normal_vector=vertices,
    kind=6,
)

edges = []
for i in range(len(vertices)):
    for dir_i, j in enumerate(sorted_neighbors[i][:3]):
        if i >= j:
            continue

        dir_i = 2 * dir_i
        dir_j = 2 * sorted_neighbors[j].index(i)

        direction_i = truncated_tetrahedron.directions(i)[dir_i]
        direction_j = truncated_tetrahedron.directions(j)[dir_j]

        curve = cubic_bezier_connect(start=(vertices[i], direction_i), end=(vertices[j], direction_j))
        edges.append((i, j, curve))


truncated_tetrahedron.paths = edges
truncated_tetrahedron.pegs = [(False, False) for _ in range(len(edges))]
