import numpy as np


def update_grid (
            grid: np.ndarray,
            poses: np.ndarray,
            delta_p: np.ndarray,
            delta_d: np.ndarray
        ):
    delta_p_mat = delta_p.reshape((-1, 3), order='F')
    poses[1:, :] += delta_p_mat
    size_w, size_h = grid.shape
    delta_d_mat = delta_d.reshape((size_h, size_w), order='F').T
    grid += delta_d_mat