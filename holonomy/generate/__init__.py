import copy
import logging
from random import choices, random

import matplotlib.pyplot as plt
import networkx as nx
from more_itertools import pairwise
from tqdm import trange

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


def path_has_splitting_bridge(G: nx.Graph, path: list[tuple[int, int]]) -> bool:
    bridges = path_bridges(G, path)

    if not bridges:
        return False

    total_nodes = G.number_of_nodes()

    for bridge in bridges:
        G_copy = G.copy()
        G_copy.remove_edge(*bridge)

        u, v = bridge

        comp_u = nx.node_connected_component(G_copy, u)
        comp_v = nx.node_connected_component(G_copy, v)

        smaller_comp_size = min(len(comp_u), len(comp_v))

        if smaller_comp_size / total_nodes >= 0.2:
            return True

    return False


def generate_pegs(network: Network, min_length: int = 0, max_iterations: int = 10000) -> Network | None:
    options = [(True, False), (False, True), (False, False)]
    solvable = False
    for _ in trange(max_iterations):
        weight = 1.0 + random() * 4.0
        pegs = choices(options, weights=[weight, weight, 1], k=len(network.paths))
        network.pegs = pegs
        graph = Graph.from_network(network, legs=(0, 1))
        solution = graph.solve()

        subgraph = graph.representation.subgraph(
            nx.node_connected_component(graph.representation, network.start),
        )

        solvable = (
            solution is not None
            and len(solution) >= min_length
            and (find_hanging_tree(subgraph) is None)
            and path_has_splitting_bridge(graph.representation, solution)
        )

        if solvable:
            return network


def draw_graph(G: nx.Graph, solution: list[tuple[int, int]] | None):
    component = nx.node_connected_component(G, (0, 0))
    subgraph = G.subgraph(component)

    pos = nx.kamada_kawai_layout(subgraph, scale=2)
    pos = nx.spring_layout(subgraph, pos=pos, k=0.5)

    node_colors = ["lightblue"] * subgraph.number_of_nodes()
    node_list = list(subgraph.nodes())
    if (0, 0) in node_list:
        node_colors[node_list.index((0, 0))] = "red"
    if (0, 1) in node_list:
        node_colors[node_list.index((0, 1))] = "purple"

    nx.draw(
        subgraph,
        pos=pos,
        with_labels=True,
        node_size=100,
        node_color=node_colors,
        font_size=10,
        edge_color="grey",
    )

    if solution is not None:
        solution_edges = list(pairwise(solution))
        nx.draw_networkx_edges(subgraph, pos=pos, edgelist=solution_edges, edge_color="red", width=2.0)

    plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    network = generate_pegs(copy.deepcopy(square_antiprism))
    assert network is not None

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

    before = Graph.from_network(dodecahedron, legs=(0, 1))
    draw_graph(graph.representation, solution)
