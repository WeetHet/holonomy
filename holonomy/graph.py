import copy
import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

import networkx as nx
import numpy as np


@dataclass
class Network:
    vertex_count: int
    paths: list[tuple[int, int, np.ndarray]]
    pegs: list[tuple[bool, bool]]
    start: tuple[int, int]  # starting vertex, starting direction
    coords: np.ndarray
    principal_vector: np.ndarray
    normal_vector: np.ndarray
    kind: int

    def directions(self, vertex: int) -> np.ndarray:
        m0, n = self.principal_vector[vertex], self.normal_vector[vertex]
        mp = np.cross(n, m0)

        return np.array([
            np.cos(2 * np.pi * i / self.kind) * m0 + np.sin(2 * np.pi * i / self.kind) * mp for i in range(self.kind)
        ])

    def direction(self, vertex: int, vector: np.ndarray) -> int:
        m0 = self.principal_vector[vertex]
        mp = np.cross(self.normal_vector[vertex], m0)

        vector = m0 * np.dot(vector, m0) + mp * np.dot(vector, mp)
        vector = vector / np.linalg.norm(vector)

        ds = self.directions(vertex)
        return int(np.argmax(np.dot(ds, vector)))

    def solve(self):
        graph = Graph.from_network(self, legs=(0, 1))
        return graph.solve()


@dataclass
class Graph:
    network: Network
    representation: nx.Graph

    @classmethod
    def clean_network(cls, network: Network) -> Network:
        network = copy.deepcopy(network)
        start_v, start_dir = network.start
        start_dir_inv = (start_dir + network.kind // 2) % network.kind

        new_paths, new_pegs = [], []
        for (u, v, path), pegs in zip(network.paths, network.pegs, strict=True):
            path_dir = network.direction(u, path[-1] - path[-2])
            if (v == start_v and path_dir == start_dir) or (u == start_v and path_dir == start_dir_inv):
                continue
            new_paths.append((u, v, path))
            new_pegs.append(pegs)

        network.paths = new_paths
        network.pegs = new_pegs
        return network

    @classmethod
    def from_network(cls, network: Network, legs: Iterable[int] = ()) -> Self:
        assert all(0 <= leg < network.kind for leg in legs), f"All legs should be in ({0}..<{network.kind}) range"

        network = cls.clean_network(network)
        representation = nx.Graph()
        representation.add_nodes_from(itertools.product(range(network.vertex_count), range(network.kind)))

        for direction in range(network.kind):
            paths_with_pegs = (
                (pegs, path) for (pegs, path) in zip(network.pegs, network.paths, strict=True) if len(path[2]) > 1
            )
            for pegs, (v_from, v_to, path) in paths_with_pegs:
                first, last = path[1] - path[0], path[-1] - path[-2]
                dir_first, dir_last = network.direction(v_from, first), network.direction(v_to, last)
                new_direction = (direction - dir_first + dir_last) % network.kind

                skip_edge = False
                for leg in legs:
                    rot_first = (leg + direction - dir_first) % network.kind
                    check_left = 0 < rot_first < network.kind // 2
                    check_right = rot_first > network.kind // 2
                    if (check_left and pegs[0]) or (check_right and pegs[1]):
                        skip_edge = True
                        break

                if not skip_edge:
                    representation.add_edge((v_from, direction), (v_to, new_direction))

        return cls(network, representation)

    def solve(self) -> list[tuple[int, int]] | None:
        graph = self.representation

        vertex, direction = self.network.start
        source, target = (vertex, direction), (vertex, (direction + 1) % self.network.kind)
        if not nx.has_path(graph, source, target):
            return None
        path = nx.shortest_path(graph, source, target)
        return path
