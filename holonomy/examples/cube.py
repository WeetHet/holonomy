import numpy as np
import plotly.graph_objects as go

from holonomy.graph import Network


def spherical_interpolation(v0, v1, num_points=30):
    arc_points = []
    for t in np.linspace(0, 1, num_points):
        p = (1 - t) * v0 + t * v1
        p /= np.linalg.norm(p)
        arc_points.append(p)
    return np.array(arc_points)


R = 1
cube_vertices = np.array([
    [1, 1, 1],
    [1, 1, -1],
    [1, -1, 1],
    [1, -1, -1],
    [-1, 1, 1],
    [-1, 1, -1],
    [-1, -1, 1],
    [-1, -1, -1],
]) / np.sqrt(3)

edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

arcs = []
principal_vector = [np.zeros(3) for _ in range(8)]

for u, v in edges:
    v0, v1 = cube_vertices[u], cube_vertices[v]
    arc = spherical_interpolation(v0, v1, num_points=30)
    arcs.append((u, v, arc))
    principal_vector[u] = arc[1] - arc[0]
    principal_vector[v] = arc[-1] - arc[-2]

for i, p in enumerate(principal_vector):
    p /= np.linalg.norm(p)
    principal_vector[i] = p

cube = Network(
    vertex_count=8,
    paths=arcs,
    pegs=[(False, False) for _ in range(len(arcs))],
    start=(0, 0),
    coords=cube_vertices,
    principal_vector=np.array(principal_vector),
    normal_vector=cube_vertices,
    kind=6,
)

if __name__ == "__main__":
    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            x=x_sphere,
            y=y_sphere,
            z=z_sphere,
            colorscale="Blues",
            opacity=0.3,
            showscale=False,
        )
    )

    for _u, _v, arc in arcs:
        fig.add_trace(
            go.Scatter3d(
                x=arc[:, 0],
                y=arc[:, 1],
                z=arc[:, 2],
                mode="lines",
                line=dict(color="red", width=5),
            )
        )

    for i, pvec in enumerate(principal_vector):
        vertex = cube_vertices[i]
        to = vertex + pvec * 0.3
        fig.add_trace(
            go.Scatter3d(
                x=np.array([vertex[0], to[0]]),
                y=np.array([vertex[1], to[1]]),
                z=np.array([vertex[2], to[2]]),
                mode="lines",
                line=dict(color="blue", width=5),
            )
        )

    fig.add_trace(
        go.Scatter3d(
            x=cube_vertices[:, 0],
            y=cube_vertices[:, 1],
            z=cube_vertices[:, 2],
            mode="text",
            text=[f"{i}" for i in range(8)],
            textposition="top center",
            textfont=dict(size=16, color="black"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        title="",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    fig.show()
