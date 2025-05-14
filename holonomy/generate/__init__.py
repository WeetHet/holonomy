import copy
import logging
from random import choices, random

import matplotlib.pyplot as plt
import networkx as nx
from more_itertools import pairwise

from holonomy.examples.dodecahedron import dodecahedron  # noqa: F401
from holonomy.examples.octahedron import octahedron  # noqa: F401
from holonomy.examples.square_antiprism import square_antiprism  # noqa: F401
from holonomy.graph import Graph, Network
from holonomy.visualise.graph import compare_views


def find_hanging_tree(G: nx.Graph, min_size=8):
    for u, v in nx.bridges(G):
        G2 = G.copy()
        G2.remove_edge(u, v)

        comp_u = nx.node_connected_component(G2, u)
        comp_v = nx.node_connected_component(G2, v)

        for comp in (comp_u, comp_v):
            if len(comp) >= min_size:
                sub = G.subgraph(comp)
                if nx.is_tree(sub):
                    return comp, (u, v)

    return None


def path_bridges(G: nx.Graph, path: list[tuple[int, int]]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    edges = list(pairwise(path))

    return list(bridge for bridge in nx.bridges(G) if bridge in edges)


def generate_pegs(network: Network, min_length: int = 0, max_iterations: int = 1000) -> Network:
    options = [(True, False), (False, True), (False, False)]
    solvable = False
    iterations = 0
    while not solvable and iterations < max_iterations:
        weight = 1.0 + random() * 4.0
        pegs = choices(options, weights=[weight, weight, 1], k=len(network.paths))
        network.pegs = pegs
        graph = Graph.from_network(network, legs=(0, 1))
        solution = graph.solve()

        nodes, edges = (
            graph.representation.number_of_nodes(),
            graph.representation.number_of_edges(),
        )

        solvable = (
            solution is not None
            and len(solution) >= min_length
            and edges / nodes >= 1.0
            and (find_hanging_tree(graph.representation) is None)
        )

        iterations += 1
        if iterations % 100 == 0:
            logging.info(f"Finished {iterations} iterations")

    logging.info(f"Generated pegs in {iterations} iterations")
    return network


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    network = generate_pegs(
        copy.deepcopy(square_antiprism),
        min_length=5,
    )

    fig = compare_views(
        network,
        nesting_type="embed",
        scale_factor=0.1,
        show_principal_vector=True,
    )
    fig.show()

    solution = network.solve()
    graph = Graph.from_network(network, legs=(0, 1))

    if solution is not None:
        print(f"Solution is {solution}, of length {len(solution)}")
        print(f"Stats: {len(path_bridges(graph.representation, solution))=}")

    pos = nx.kamada_kawai_layout(graph.representation, scale=2)
    pos = nx.spring_layout(graph.representation, pos=pos, k=0.5)
    nx.draw(graph.representation, pos=pos, with_labels=True, node_size=100, node_color="lightblue", font_size=10)
    plt.show()
