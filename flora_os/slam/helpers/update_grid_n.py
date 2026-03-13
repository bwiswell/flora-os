import numpy as np

from ..config import Config

from .util import rotation_matrix


def update_grid_n (
            poses: np.ndarray,
            scan_xy: list[np.ndarray]
        ) -> np.ndarray:
    n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
    n_poses = poses.shape[0]
    for i in range(n_poses):
        r_i = rotation_matrix(poses[i, 2])
        scan_xy_i = scan_xy[i].reshape((2, -1), order='F')
        pose_vec = poses[i, :2].T
        s_i = (r_i @ scan_xy_i) + pose_vec
        xy = (s_i / Config.SCALE).round().astype(np.int32)
        temp_n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
        for j in range(xy.shape[1]):
            row, col = xy[0, j], xy[1, j]
            temp_n[row, col] += 1
        n += temp_n
    return n