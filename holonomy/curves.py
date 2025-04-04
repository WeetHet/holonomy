import bezier
import numpy as np


def cubic_bezier_connect(
    start: (np.ndarray, np.ndarray),
    end: (np.ndarray, np.ndarray),
    num_points: int = 100,
) -> np.ndarray:
    points = np.stack((*start, *end)).T
    curve = bezier.Curve(np.asfortranarray(points), degree=3)
    return curve.evaluate_multi(np.linspace(0, 1, num_points))
