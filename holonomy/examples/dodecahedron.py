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
# g_r = golden ratio
g_r = (1 + np.sqrt(5)) / 2
dodecahedron_vertices = np.array([
    [-1, -1, -1],
    [-1, -1, 1],
    [-1, 1, -1],
    [-1, 1, 1],
    [1, -1, -1],
    [1, -1, 1],
    [1, 1, -1],
    [1, 1, 1],
    [0, -g_r, -1 / g_r],
    [0, -g_r, 1 / g_r],
    [0, g_r, -1 / g_r],
    [0, g_r, 1 / g_r],
    [-g_r, -1 / g_r, 0],
    [-g_r, 1 / g_r, 0],
    [g_r, -1 / g_r, 0],
    [g_r, 1 / g_r, 0],
    [-1 / g_r, 0, -g_r],
    [-1 / g_r, 0, g_r],
    [1 / g_r, 0, -g_r],
    [1 / g_r, 0, g_r],
]) / np.sqrt(3)

edges = [
    (0, 8),
    (0, 12),
    (0, 16),
    (1, 9),
    (1, 12),
    (1, 17),
    (2, 10),
    (2, 13),
    (2, 16),
    (3, 11),
    (3, 13),
    (3, 17),
    (4, 8),
    (4, 14),
    (4, 18),
    (5, 9),
    (5, 14),
    (5, 19),
    (6, 10),
    (6, 15),
    (6, 18),
    (7, 11),
    (7, 15),
    (7, 19),
    (8, 9),
    (10, 11),
    (12, 13),
    (14, 15),
    (16, 18),
    (17, 19),
]

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

arcs = []
principal_vector = [np.zeros(3) for _ in range(20)]

for u, v in edges:
    v0, v1 = dodecahedron_vertices[u], dodecahedron_vertices[v]
    arc = spherical_interpolation(v0, v1, num_points=30)
    arcs.append((u, v, arc))
    principal_vector[u] = arc[1] - arc[0]
    principal_vector[v] = arc[-1] - arc[-2]

for i, p in enumerate(principal_vector):
    p /= np.linalg.norm(p)
    principal_vector[i] = p

dodecahedron = Network(
    vertex_count=20,
    paths=arcs,
    coords=dodecahedron_vertices,
    principal_vector=np.array(principal_vector),
    normal_vector=dodecahedron_vertices,
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
        vertex = dodecahedron_vertices[i]
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
            x=dodecahedron_vertices[:, 0],
            y=dodecahedron_vertices[:, 1],
            z=dodecahedron_vertices[:, 2],
            mode="text",
            text=[f"{i}" for i in range(20)],
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
