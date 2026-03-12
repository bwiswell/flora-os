import math

import numpy as np


def bilinear_interpolation (grid: np.ndarray, xy: np.ndarray) -> np.ndarray:
    n_pts = xy.shape[0]
    inter = np.ndarray((n_pts), np.float64)
    for i in range(n_pts):
        x = xy[i, 0]
        y = xy[i, 1]
        i_a = math.floor(y)
        i_b = i_a + 1
        j_a = math.floor(x)
        j_b = j_a + 1
        if i_a < 0 or i_b >= grid.shape[0] or \
                j_a < 0 or j_b >= grid.shape[1]:
            inter[i] = 0.0
            continue
        q_a_a = grid[i_a, j_a]
        q_b_a = grid[i_a, j_b]
        q_a_b = grid[i_b, j_a]
        q_b_b = grid[i_b, j_b]
        w_a = (j_b - x) * q_a_a + (x - j_a) * q_b_a
        w_b = (j_b - x) * q_a_b + (x - j_a) * q_b_b
        w = (i_b - y) * w_a + (y - i_a) * w_b
        inter[i] = w
    return inter