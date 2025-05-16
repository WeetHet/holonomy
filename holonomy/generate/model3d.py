from dataclasses import astuple, dataclass

import numpy as np
import trimesh
from trimesh.geometry import triangulate_quads

from holonomy.examples.tetrahedron import tetrahedron
from holonomy.graph import Network


@dataclass
class SectionConfig:
    height: float
    width: float
    rail_height: float
    rail_width: float
    bottleneck_height: float
    bottleneck_width: float

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class PegsConfig:
    height: float
    radius: float

    def __iter__(self):
        return iter(astuple(self))


def create_groove_section(parameters: SectionConfig) -> np.ndarray:
    h, w, g_h, g_w, bn_h, bn_w = parameters

    outline = np.array([
        [-bn_w / 2, 0],
        [-bn_w / 2, -bn_h],
        [-w / 2, -bn_h],
        [-w / 2, -bn_h - h],
        [-g_w / 2, -bn_h - h],
        [-g_w / 2, -bn_h - h + g_h],
        [g_w / 2, -bn_h - h + g_h],
        [g_w / 2, -bn_h - h],
        [w / 2, -bn_h - h],
        [w / 2, -bn_h],
        [bn_w / 2, -bn_h],
        [bn_w / 2, 0],
    ])
    return outline


def compute_tangents(points: np.ndarray) -> np.ndarray:
    tangents = [None] * len(points)

    tangents[0] = points[1] - points[0]
    tangents[0] /= np.linalg.norm(tangents[0])
    for i in range(1, len(points) - 1):
        p_prev = points[i - 1]
        p_next = points[i + 1]
        tangent = p_next - p_prev
        tangent /= np.linalg.norm(tangent)
        tangents[i] = tangent

    tangents[-1] = points[-1] - points[-2]
    tangents[-1] /= np.linalg.norm(tangents[-1])

    return np.array(tangents)


def construct_groove_using_sections(path: np.ndarray, section: np.ndarray) -> trimesh.Trimesh:
    points = path
    tangents = compute_tangents(points)
    sections = []
    n1 = points / np.linalg.norm(points, axis=-1, keepdims=True)
    n2 = np.cross(tangents, n1)

    s0 = section[:, 0]
    s1 = section[:, 1]

    sections = points[:, None, :] + s0[None, :, None] * n2[:, None, :] + s1[None, :, None] * n1[:, None, :]
    P, C, _ = sections.shape
    vertices = sections.reshape(P * C, 3)
    faces = [
        [p * C + c, (p + 1) * C + c, (p + 1) * C + (c + 1) % C, p * C + (c + 1) % C]
        for p in range(P - 1)
        for c in range(C)
    ]
    side1 = [[0, 1, 10, 11], [2, 3, 4, 5], [1, 2, 5], [1, 5, 10], [5, 6, 9, 10], [5, 6, 9, 10], [6, 7, 8, 9]]
    n = P * C - 12
    side2 = [
        [n, n + 1, n + 10, n + 11],
        [n + 2, n + 3, n + 4, n + 5],
        [n + 1, n + 2, n + 5],
        [n + 1, n + 5, n + 10],
        [n + 5, n + 6, n + 9, n + 10],
        [n + 5, n + 6, n + 9, n + 10],
        [n + 6, n + 7, n + 8, n + 9],
    ]
    faces += side1
    faces += [s[::-1] for s in side2]
    groove = trimesh.Trimesh(vertices, triangulate_quads(faces))
    groove.update_faces(groove.unique_faces())
    return groove


def construct_grooves(network: Network, section: np.ndarray) -> list[trimesh.Trimesh]:
    return [construct_groove_using_sections(path, section) for _, _, path in network.paths]


def cylinder_intersections(config: SectionConfig, network: Network) -> list[trimesh.Trimesh]:
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=1.0 - config.bottleneck_height - config.height)

    centers = network.coords
    radius = (config.width**2 + config.rail_width**2) ** 0.5 / 2
    height = config.rail_height * 2
    offset = config.bottleneck_height + config.height - config.rail_height / 2
    cylinders = []
    for center in centers:
        direction = np.array(center)
        norm = np.linalg.norm(direction)
        if norm == 0:
            offset_vec = np.zeros(3)
        else:
            direction = direction / norm
            offset_vec = -direction * offset

        center = np.array(center) + offset_vec

        cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
        T_align = trimesh.geometry.align_vectors([0, 0, 1], direction)
        cyl.apply_transform(T_align)

        T_move = trimesh.transformations.translation_matrix(center)
        cyl.apply_transform(T_move)
        cylinders.append(trimesh.boolean.difference([cyl, sphere]))

    return cylinders


def add_pegs(network: Network, pegs_config: PegsConfig, section_config: SectionConfig) -> list[trimesh.Trimesh]:
    peg_meshes = []
    offset_distance = section_config.width / 2
    radius = float(pegs_config.radius)
    height = pegs_config.height

    for (has_left, has_right), (_, _, path) in zip(network.pegs, network.paths, strict=True):
        mid_point = path[len(path) // 2]

        tangent = compute_tangents(path)[len(path) // 2]
        normal = mid_point / np.linalg.norm(mid_point)

        side_vector = np.cross(normal, tangent)
        side_vector /= np.linalg.norm(side_vector)

        for direction, present in zip([-1, 1], [has_left, has_right], strict=True):
            if not present:
                continue

            peg_center = mid_point + direction * offset_distance * side_vector

            peg = trimesh.creation.cylinder(radius=radius, height=height, sections=network.kind)
            align_matrix = trimesh.geometry.align_vectors([0, 0, 1], normal)
            peg.apply_transform(align_matrix)

            translation = trimesh.transformations.translation_matrix(peg_center)
            peg.apply_transform(translation)

            peg_meshes.append(peg)

    return peg_meshes


if __name__ == "__main__":
    network = tetrahedron
    network.pegs = [(True, True) for _ in range(len(network.paths))]

    sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.98)
    config = SectionConfig(
        height=0.2,
        width=0.35,
        rail_height=0.1,
        rail_width=0.06,
        bottleneck_height=0.08,
        bottleneck_width=0.16,
    )

    pegs_config = PegsConfig(height=0.1, radius=0.05)
    peg_meshes = add_pegs(network, pegs_config, config)
    sphere = trimesh.boolean.union([sphere, *peg_meshes])
    section = create_groove_section(config)
    grooves = construct_grooves(network, section)

    cylinders = cylinder_intersections(config, network)

    sphere = trimesh.boolean.difference([sphere, *grooves, *cylinders])
    sphere.show()
