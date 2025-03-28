import numpy as np
import plotly.graph_objects as go

def spherical_interpolation(v0, v1, num_points=30):
    arc_points = []
    for t in np.linspace(0, 1, num_points):
        p = (1 - t) * v0 + t * v1
        p /= np.linalg.norm(p)
        arc_points.append(p)
    return np.array(arc_points)

R = 1
tetrahedron_vertices = np.array([
    [1,  1,  1],
    [-1, -1,  1],
    [-1,  1, -1],
    [1,  -1, -1]
]) / np.sqrt(3)

edges = [
    (0, 1), (0, 2), (0, 3),
    (1, 2), (1, 3), (2, 3)
]

fig = go.Figure()

theta = np.linspace(0, np.pi, 40)
phi = np.linspace(0, 2 * np.pi, 40)
theta_grid, phi_grid = np.meshgrid(theta, phi)

x_sphere = R * np.sin(theta_grid) * np.cos(phi_grid)
y_sphere = R * np.sin(theta_grid) * np.sin(phi_grid)
z_sphere = R * np.cos(theta_grid)

fig.add_trace(go.Surface(
    x=x_sphere, y=y_sphere, z=z_sphere,
    colorscale='Blues',
    opacity=0.3,
    showscale=False
))

faces = [
    [0, 1, 2],
    [0, 1, 3],
    [0, 2, 3],
    [1, 2, 3]
]
for face in faces:
    x_tet = [tetrahedron_vertices[i, 0] for i in face] + [tetrahedron_vertices[face[0], 0]]
    y_tet = [tetrahedron_vertices[i, 1] for i in face] + [tetrahedron_vertices[face[0], 1]]
    z_tet = [tetrahedron_vertices[i, 2] for i in face] + [tetrahedron_vertices[face[0], 2]]

    fig.add_trace(go.Scatter3d(x=x_tet, y=y_tet, z=z_tet, mode='lines', line=dict(color='green', width=5)))

for edge in edges:
    v0, v1 = tetrahedron_vertices[edge[0]], tetrahedron_vertices[edge[1]]
    arc = spherical_interpolation(v0, v1, num_points=30)
    fig.add_trace(go.Scatter3d(
        x=arc[:, 0], y=arc[:, 1], z=arc[:, 2],
        mode='lines', line=dict(color='red', width=5)
    ))

fig.update_layout(
    title="",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
    ),
    margin=dict(l=0, r=0, b=0, t=0)
)


fig.show()