import numpy as np

from holonomy.curves import cubic_bezier_connect
from holonomy.graph import Network

top_square = []
bottom_square = []

top_rotate = 0
for i in range(4):
    angle_top = i * (2 * np.pi / 4)
    top_square.append([np.cos(angle_top), np.sin(angle_top), 1])

    angle_bottom = angle_top + top_rotate
    bottom_square.append([np.cos(angle_bottom), np.sin(angle_bottom), -1])

vertices = np.array(top_square + bottom_square)
top_edges = [(i, (i + 1) % 4) for i in range(4)]
bottom_edges = [(i + 4, (i + 1) % 4 + 4) for i in range(4)]

connecting_edges = []
for i in range(4):
    connecting_edges.append((i, (i + 4)))
    connecting_edges.append((i, ((i + 1) % 4 + 4)))


edges = top_edges + bottom_edges + connecting_edges
neighbors = [[] for _ in range(len(vertices))]
for i, j in edges:
    neighbors[i].append(j)
    neighbors[j].append(i)


sorted_neighbors = [[] for _ in range(len(vertices))]
for i in range(len(vertices)):
    vertex_neighbors = neighbors[i]
    if not vertex_neighbors:
        continue

    ref_vec = vertices[vertex_neighbors[0]] - vertices[i]
    ref_vec = ref_vec / np.linalg.norm(ref_vec)

    normal = vertices[i]
    normal = normal / np.linalg.norm(normal)

    x_axis = np.cross(normal, ref_vec)
    x_axis = x_axis / np.linalg.norm(x_axis)

    y_axis = np.cross(normal, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)

    angles = []
    for j in vertex_neighbors:
        proj_vec = vertices[j] - vertices[i]
        proj_vec = proj_vec - np.dot(proj_vec, normal) * normal
        if np.linalg.norm(proj_vec) > 1e-10:
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
    if not sorted_neighbors[i]:
        principal_vector.append(np.zeros(3))
        continue

    first_neighbor = sorted_neighbors[i][0]

    direction = vertices[first_neighbor] - vertices[i]

    normal_i = vertices[i].copy()
    radial_component = np.dot(direction, normal_i) * normal_i
    tangential_direction = direction - radial_component

    if np.linalg.norm(tangential_direction) > 1e-10:
        tangential_direction = tangential_direction / np.linalg.norm(tangential_direction)
    principal_vector.append(tangential_direction)

principal_vector = np.array(principal_vector)
square_antiprism = Network(
    vertex_count=len(vertices),
    paths=[],
    pegs=[],
    start=(0, 0),
    coords=vertices,
    principal_vector=principal_vector,
    normal_vector=vertices,
    kind=4,
)

bezier_edges = []
for i in range(len(vertices)):
    for dir_i, j in enumerate(sorted_neighbors[i][:4]):
        if i >= j:
            continue

        dir_j = sorted_neighbors[j].index(i)

        direction_i = square_antiprism.directions(i)[dir_i]
        direction_j = square_antiprism.directions(j)[dir_j]

        curve_points = cubic_bezier_connect(start=(vertices[i], direction_i), end=(vertices[j], direction_j))
        bezier_edges.append((i, j, curve_points))

square_antiprism.paths = bezier_edges
square_antiprism.pegs = [(False, False) for _ in range(len(bezier_edges))]
