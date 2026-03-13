import math

import numpy as np


def d_rotation_matrix (theta: float) -> np.ndarray:
        c, s = math.cos(theta), math.sin(theta)
        return np.array([[-s, c], [-c, -s]])


def rotation_matrix (theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s], [s, c]])


def wrap_radians (val: float) -> float:
    r = val
    while r < -math.pi:
        r += 2 * math.pi
    while r > math.pi:
        r -= 2 * math.pi
    return r