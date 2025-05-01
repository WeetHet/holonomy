import networkx as nx

from holonomy.examples.octahedron import octahedron
from holonomy.graph import Graph


def main():
    octahedron_graph = Graph.from_network(octahedron, legs=[0])
    for component in nx.connected_components(octahedron_graph.representation):
        print(component)

    print(octahedron_graph.solve())


if __name__ == "__main__":
    main()
