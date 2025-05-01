import bezier
import numpy as np
from typing import Any
import scipy


def curvature(points: np.ndarray) -> np.floating[Any]:
    dp = (points[2:] - points[:-2]) / 2
    ddp = points[2:] + points[:-2] - 2 * points[1:-1]

    num = np.linalg.norm(np.cross(dp, ddp, axis=1), axis=1)
    denom = np.linalg.norm(dp, axis=1) ** 3
    return num / denom


def cubic_bezier_connect(
    start: (np.ndarray, np.ndarray),
    end: (np.ndarray, np.ndarray),
    num_points: int = 100,
) -> np.ndarray:
    p0, d0 = start
    p3, d3 = end

    d0 /= np.linalg.norm(d0)
    d3 /= np.linalg.norm(d3)

    def objective(x: np.ndarray) -> float:
        alpha, beta = x
        p1 = p0 + alpha * d0
        p2 = p3 + beta * d3
        nodes = np.asfortranarray(np.stack([p0, p1, p2, p3], axis=1))
        t_vals = np.linspace(0, 1, num_points)

        points = bezier.Curve(nodes, degree=3).evaluate_multi(t_vals).T
        points /= np.linalg.norm(points, axis=1, keepdims=True)

        curvature_values = curvature(points)
        maximum_curvature = np.max(curvature_values)
        return maximum_curvature


    res = scipy.optimize.direct(
        objective,
        bounds=[(0.01, 1.0), (0.01, 1.0)],
    )
    alpha_opt, beta_opt = res.x

    p1 = p0 + alpha_opt * d0
    p2 = p3 + beta_opt * d3
    points = np.stack([p0, p1, p2, p3], axis=1)
    curve = bezier.Curve(np.asfortranarray(points), degree=3)
    return curve.evaluate_multi(np.linspace(0, 1, num_points)).T
