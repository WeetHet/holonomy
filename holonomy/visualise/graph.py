import itertools

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from holonomy.examples.dodecahedron import dodecahedron  # noqa: F401
from holonomy.examples.octahedron import octahedron  # noqa: F401
from holonomy.examples.tetrahedron import tetrahedron  # noqa: F401
from holonomy.graph import Graph, Network


def visualize_graph(
    graph: Graph,
    scale_factor=0.3,
    show_network=True,
    show_graph=True,
    show_principal_vector=True,
    show_pegs=True,
    nesting_type="circle",
    network_color="red",
    graph_color="purple",
):
    network = graph.network
    vertex_count = network.vertex_count
    kind = network.kind

    fig = go.Figure()

    R = 1
    theta = np.linspace(0, np.pi, 40)
    phi = np.linspace(0, 2 * np.pi, 40)
    theta_grid, phi_grid = np.meshgrid(theta, phi)

    x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
    y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
    z_sphere = R * np.cos(theta_grid)

    if show_network:
        fig.add_trace(
            go.Surface(
                x=x_sphere,
                y=y_sphere,
                z=z_sphere,
                colorscale="Blues",
                opacity=0.2,
                showscale=False,
            )
        )

    nested_coords = {}

    for vertex in range(vertex_count):
        base_coord = network.coords[vertex]
        directions = network.directions(vertex)

        for direction in range(kind):
            match nesting_type:
                case "circle":
                    nested_coord = base_coord * (1 - scale_factor) + directions[direction] * scale_factor
                case "embed":
                    nested_coord = base_coord * (0.1 + (direction + 1) / kind * (0.9 - scale_factor))
                case _:
                    raise ValueError(f"Invalid nesting type: {nesting_type}. Supported types are 'circle' and 'embed'.")
            nested_coords[(vertex, direction)] = nested_coord

    nested_x, nested_y, nested_z, nested_text = [], [], [], []
    for vertex in range(vertex_count):
        for direction in range(kind):
            coord = nested_coords[(vertex, direction)]
            nested_x.append(coord[0])
            nested_y.append(coord[1])
            nested_z.append(coord[2])
            nested_text.append(f"{vertex}-{direction}")

    if show_graph:
        fig.add_trace(
            go.Scatter3d(
                x=nested_x,
                y=nested_y,
                z=nested_z,
                mode="markers",
                marker=dict(size=6, color="green", opacity=0.8),
                text=nested_text,
                hoverinfo="text",
                name="Nested vertices",
            )
        )

        for edge in graph.representation.edges():
            v1, v2 = edge
            coord1, coord2 = nested_coords[v1], nested_coords[v2]

            fig.add_trace(
                go.Scatter3d(
                    x=[coord1[0], coord2[0]],
                    y=[coord1[1], coord2[1]],
                    z=[coord1[2], coord2[2]],
                    mode="lines",
                    line=dict(color=graph_color, width=2),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

    if show_network:
        for _, _, arc in network.paths:
            fig.add_trace(
                go.Scatter3d(
                    x=arc[:, 0],
                    y=arc[:, 1],
                    z=arc[:, 2],
                    mode="lines",
                    line=dict(color=network_color, width=4),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

        fig.add_trace(
            go.Scatter3d(
                x=network.coords[:, 0],
                y=network.coords[:, 1],
                z=network.coords[:, 2],
                mode="markers+text",
                marker=dict(size=8, color="red", opacity=1),
                text=[f"{i}" for i in range(vertex_count)],
                textposition="top center",
                textfont=dict(size=16, color="black"),
                hoverinfo="text",
                name="Network vertices",
            )
        )

        if show_principal_vector:
            for vertex in range(vertex_count):
                base_coord = network.coords[vertex]
                directions = network.directions(vertex)
                first_direction = directions[0] * 0.5
                end_coord = base_coord + first_direction

                fig.add_trace(
                    go.Scatter3d(
                        x=[base_coord[0], end_coord[0]],
                        y=[base_coord[1], end_coord[1]],
                        z=[base_coord[2], end_coord[2]],
                        mode="lines",
                        line=dict(color="blue", width=3),
                        hoverinfo="none",
                        name="Principal vector" if vertex == 0 else None,
                        showlegend=vertex == 0,
                    )
                )

        if show_pegs:
            place_pegs_left, place_pegs_right = [], []
            for (u, v, _), (left, right) in zip(network.paths, network.pegs, strict=True):
                if left:
                    place_pegs_left.append((u, v))
                if right:
                    place_pegs_right.append((u, v))

            coeff_left = zip(itertools.repeat(1), place_pegs_left)
            coeff_right = zip(itertools.repeat(-1), place_pegs_right)
            for c, (u, v) in itertools.chain(coeff_left, coeff_right):
                arc = next((arc for arc in network.paths if arc[:2] == (u, v)), None)
                assert arc is not None, f"Attemted to place a peg at ({u}, {v}) but this path doesn't exist"
                _, _, path = arc
                mid_idx = len(path) // 2
                midpoint, nxt = path[mid_idx], path[mid_idx + 1]
                mid_vector = nxt - midpoint

                mp = np.cross(midpoint, mid_vector)
                mp = mp / np.linalg.norm(mp)

                peg_distance = 0.1
                point = midpoint + c * mp * peg_distance

                up, down = point * 1.1, point * 0.9

                fig.add_trace(
                    go.Scatter3d(
                        x=np.array([up[0], down[0]]),
                        y=np.array([up[1], down[1]]),
                        z=np.array([up[2], down[2]]),
                        mode="lines",
                        line=dict(color="green", width=5),
                    )
                )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return fig


def visualize_network_and_graph(network: Network, nesting_type="circle", scale_factor=0.3):
    graph = Graph.from_network(network, legs=[0])
    return visualize_graph(graph, nesting_type=nesting_type, scale_factor=scale_factor)


def compare_views(
    network: Network,
    nesting_type="circle",
    scale_factor=0.3,
    show_principal_vector=True,
    show_pegs=True,
):
    graph = Graph.from_network(network)

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "scene"}, {"type": "scene"}]],
        subplot_titles=("Original Network", "Graph Representation"),
    )

    network_fig = visualize_graph(
        graph,
        nesting_type=nesting_type,
        scale_factor=0,
        show_graph=False,
        show_network=True,
        show_pegs=show_pegs,
        show_principal_vector=show_principal_vector,
    )
    for trace in network_fig.data:
        fig.add_trace(trace, row=1, col=1)

    graph_fig = visualize_graph(
        graph,
        nesting_type=nesting_type,
        scale_factor=scale_factor,
        show_network=False,
        show_pegs=show_pegs,
        show_principal_vector=show_principal_vector,
    )
    for trace in graph_fig.data:
        fig.add_trace(trace, row=1, col=2)

    fig.update_layout(
        height=600,
        width=1200,
        title_text="Network and Graph Comparison",
    )

    return fig


def main():
    network = octahedron
    nesting_type = "circle"
    scale_factor = 0.1

    fig = visualize_network_and_graph(network, nesting_type=nesting_type, scale_factor=scale_factor)
    fig.show()

    compare_fig = compare_views(network, nesting_type=nesting_type, scale_factor=scale_factor)
    compare_fig.show()


if __name__ == "__main__":
    main()
