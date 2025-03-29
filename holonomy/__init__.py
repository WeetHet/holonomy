import networkx as nx

from holonomy.examples.tetrahedron import tetrahedron
from holonomy.graph import Graph


def main():
    tetrahedron_graph = Graph.from_network(tetrahedron)
    for component in nx.connected_components(tetrahedron_graph.representation):
        print(component)


if __name__ == "__main__":
    main()
