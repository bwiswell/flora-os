import numpy as np

from ..config import Config

from .rotate_and_scale import rotate_and_scale


def update_grid_n (
            poses: np.ndarray,
            scan_xy: list[np.ndarray]
        ) -> np.ndarray:
    n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
    n_poses = poses.shape[0]
    for i in range(n_poses):
        _, xy = rotate_and_scale(poses[i], scan_xy[i])
        temp_n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
        for j in range(xy.shape[1]):
            row, col = xy[0, j], xy[1, j]
            temp_n[row, col] += 1
        n += temp_n
    return n