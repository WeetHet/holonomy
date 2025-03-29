import numpy as np


def compute_perpendicular_vector(v0, v1, centroid):
    edge_dir = v1 - v0
    edge_dir_normalized = edge_dir / np.linalg.norm(edge_dir)
    midpoint = (v0 + v1) / 2
    centroid_to_midpoint = midpoint - centroid
    centroid_to_midpoint_normalized = centroid_to_midpoint / np.linalg.norm(centroid_to_midpoint)

    perp_dir = np.cross(edge_dir_normalized, centroid_to_midpoint_normalized)
    perp_dir_normalized = perp_dir / np.linalg.norm(perp_dir)
    return perp_dir_normalized


def sinusoidal_modulation(v0, v1, centroid, num_points=50, amplitude=0.2):
    t = np.linspace(0, 1, num_points)
    edge_vector = v1 - v0
    perp_dir = compute_perpendicular_vector(v0, v1, centroid)
    points = []
    for t_i in t:
        point = v0 + t_i * edge_vector
        offset = amplitude * np.sin(2 * np.pi * t_i) * perp_dir
        points.append(point + offset)
    return np.array(points)


def project_onto_sphere(curve, radius=1):
    norms = np.linalg.norm(curve, axis=1).reshape(-1, 1)
    return curve / norms * radius


tetrahedron_vertices = np.array([
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, -1],
    [1, -1, -1],
]) / np.sqrt(3)

edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

centroid = np.mean(tetrahedron_vertices, axis=0)

if __name__ == "__main__":
    import plotly.graph_objects as go

    fig = go.Figure()

    theta = np.linspace(0, np.pi, 40)
    phi = np.linspace(0, 2 * np.pi, 40)
    theta_grid, phi_grid = np.meshgrid(theta, phi)

    R = 1
    x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
    y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
    z_sphere = R * np.cos(theta_grid)

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

    for edge in edges:
        v0, v1 = tetrahedron_vertices[edge[0]], tetrahedron_vertices[edge[1]]
        curve = sinusoidal_modulation(v0, v1, centroid, amplitude=0.2)
        fig.add_trace(
            go.Scatter3d(
                x=curve[:, 0],
                y=curve[:, 1],
                z=curve[:, 2],
                mode="lines",
                line=dict(color="green", width=4),
                name="Period of sin(x)",
            )
        )

    for edge in edges:
        v0, v1 = tetrahedron_vertices[edge[0]], tetrahedron_vertices[edge[1]]
        curve = sinusoidal_modulation(v0, v1, centroid, amplitude=0.2)
        projected_curve = project_onto_sphere(curve, R)
        fig.add_trace(
            go.Scatter3d(
                x=projected_curve[:, 0],
                y=projected_curve[:, 1],
                z=projected_curve[:, 2],
                mode="lines",
                line=dict(color="red", width=4),
                name="Projected edge",
            )
        )

    fig.update_layout(
        title="",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False,
    )

    fig.show()
