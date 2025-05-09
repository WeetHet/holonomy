import copy
import logging
from random import choices

import matplotlib.pyplot as plt
import networkx as nx

from holonomy.examples.dodecahedron import dodecahedron  # noqa: F401
from holonomy.examples.octahedron import octahedron  # noqa: F401
from holonomy.graph import Graph, Network
from holonomy.visualise.graph import compare_views


def generate_pegs(
    network: Network,
    min_length: int = 0,
) -> Network:
    options = [(True, False), (False, True), (False, False)]
    solvable = False
    iterations = 0
    while not solvable:
        pegs = choices(options, weights=[5, 5, 1], k=len(network.paths))
        network.pegs = pegs
        solution = network.solve()
        solvable = solution is not None and len(solution) >= min_length
        iterations += 1

    logging.info(f"Generated pegs in {iterations} iterations")
    return network


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    network = generate_pegs(
        copy.deepcopy(dodecahedron),
        min_length=10,
    )

    fig = compare_views(
        network,
        nesting_type="embed",
        scale_factor=0.1,
        show_principal_vector=True,
    )
    fig.show()

    solution = network.solve()
    assert solution is not None

    print(f"Solution is {solution}, of length {len(solution)}")

    graph = Graph.from_network(network, legs=(0, 1))
    pos = nx.kamada_kawai_layout(graph.representation, scale=2)
    pos = nx.spring_layout(graph.representation, pos=pos, k=0.5)
    nx.draw(graph.representation, pos=pos, with_labels=True, node_size=100, node_color="lightblue", font_size=10)
    plt.show()
