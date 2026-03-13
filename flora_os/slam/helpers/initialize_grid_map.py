import numpy as np

from ..config import Config

from .rotate_and_scale import rotate_and_scale


def initialize_grid_map (
            poses: np.ndarray,
            scan_xy: list[np.ndarray],
            scan_odd: list[np.ndarray]
        ) -> tuple[np.ndarray, np.ndarray]:
    grid = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
    n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
    
    for i, (xy_i, odd_i) in enumerate(zip(scan_xy, scan_odd)):
        _, xy = rotate_and_scale(poses[i], xy_i)
        temp_grid = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
        temp_n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)

        for j in range(odd_i.shape[0]):
            col, row, val = xy[0, j], xy[1, j], odd_i[j]
            temp_grid[row, col] += val
            temp_n[row, col] += 1

        grid += temp_grid
        n += temp_n
    
    return grid, n