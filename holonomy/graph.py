import itertools
from dataclasses import dataclass

import networkx as nx
import numpy as np


@dataclass
class Network:
    vertex_count: int
    paths: list[tuple[int, int, np.ndarray]]
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


@dataclass
class Graph:
    network: Network
    representation: nx.Graph

    @classmethod
    def from_network(cls, network: Network) -> "Graph":
        representation = nx.Graph()
        representation.add_nodes_from(itertools.product(range(network.vertex_count), range(network.kind)))

        for direction in range(network.kind):
            for v_from, v_to, path in filter(lambda p: len(p[2]) >= 2, network.paths):
                first, last = path[1] - path[0], path[-1] - path[-2]
                dir_first, dir_last = network.direction(v_from, first), network.direction(v_to, last)
                new_direction = (direction - dir_first + dir_last) % network.kind
                representation.add_edge((v_from, direction), (v_to, new_direction))

        return cls(network, representation)
