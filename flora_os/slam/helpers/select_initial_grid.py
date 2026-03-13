import numpy as np
import scipy.sparse as sp

from ..config import Config

from .rotate_and_scale import rotate_and_scale


def select_initial_grid (
            poses: np.ndarray,
            sel_scan_xy: list[np.ndarray],
            sel_scan_odd: list[np.ndarray]
        ) -> tuple[np.ndarray, np.ndarray]:
    rows = []
    cols = []
    grid_vals = []
    n_vals = []

    for i in range(poses.shape[0]):
        scan_xy_i = sel_scan_xy[i]
        scan_odd_i = sel_scan_odd[i]
        _, xy = rotate_and_scale(poses[i], scan_xy_i)
        cont_row = xy[1, :]
        cont_col = xy[0, :]
        row = np.floor(cont_row)
        col = np.floor(cont_col)

        a_a = cont_col - col
        a_b = col + 1 - cont_col
        b_a = cont_row - row
        b_b = row + 1 - cont_row

        w_a_a = a_b * b_b
        w_b_a = a_a * b_b
        w_a_b = a_b * b_a
        w_b_b = b_b * b_b
        
        rows_i = np.concatenate([row, row, row + 1, row + 1])
        cols_i = np.concatenate([col, col + 1, col, col + 1])

        grid_vals_i = np.concatenate([
            w_a_a * scan_odd_i,
            w_b_a * scan_odd_i,
            w_a_b * scan_odd_i,
            w_b_b * scan_odd_i
        ])
        n_vals_i = np.concatenate([w_a_a, w_b_a, w_a_b, w_b_b])

        mask = (rows_i >= 0) & (rows_i < Config.SIZE_W) & \
                (cols_i >= 0) & (cols_i < Config.SIZE_H)
        
        rows.append(rows_i[mask])
        cols.append(cols_i[mask])
        grid_vals.append(grid_vals_i[mask])
        n_vals.append(n_vals_i[mask])

    rows = np.concatenate(rows)
    cols = np.concatenate(cols)

    grid = sp.csr_matrix(
        (np.concatenate(grid_vals), (rows, cols)),
        shape=(Config.SIZE_W, Config.SIZE_H)
    ).toarray()
    n = sp.csr_matrix(
        (np.concatenate(n_vals), (rows, cols)),
        shape=(Config.SIZE_W, Config.SIZE_H)
    ).toarray()

    return grid, n