import numpy as np
import scipy.sparse as sp

from ..config import Config

from .util import rotation_matrix


def select_scan (
            poses: np.ndarray,
            scan_xy: list[np.ndarray],
            scan_odd: list[np.ndarray],
            sel_id: np.ndarray
        ) -> tuple[list[np.ndarray], list[np.ndarray]]:
    sel_row_id = sel_id[:, 0]
    sel_col_id = sel_id[:, 1]
    ones = np.ones((len(sel_row_id)), np.int32)
    grid_mask = sp.coo_matrix(
        (ones, (sel_row_id, sel_col_id)),
        shape=(Config.SIZE_W, Config.SIZE_H),
        dtype=np.int32
    )
    arr_mask = grid_mask.toarray().flatten(order='F')

    sel_scan_xy: list[np.ndarray] = []
    sel_scan_odd: list[np.ndarray] = []

    for i in range(poses.shape[0]):
        scan_odd_i = scan_odd[i]
        r_i = rotation_matrix(poses[i, 2])
        scan_xy_i = scan_xy[i]
        scan_xy_i_mat = scan_xy_i.reshape((2, -1), order='F')
        pose_vec = poses[i, :2].T
        s_i = (r_i @ scan_xy_i_mat) + pose_vec
        xy = (s_i / Config.SCALE).round().astype(np.int32)
        row = xy[1, :]
        col = xy[0, :]
        id = col * Config.SIZE_W + row
        val_i = arr_mask[id]
        id_obs = np.where(val_i == 1)[0]
        sel_scan_xy_i = np.ndarray((id_obs.size * 2), np.float64)
        sel_scan_odd_i = np.ndarray((id_obs.size), np.float64)
        for j in range(id_obs.size):
            odd_id = id_obs[j]
            xy_id = 2 * odd_id
            sel_scan_odd_i[j] = scan_odd_i[odd_id]
            sel_scan_xy_i[2 * j] = scan_xy_i[xy_id]
            sel_scan_xy_i[2 * j + 1] = scan_xy_i[xy_id + 1]
        sel_scan_xy.append(sel_scan_xy_i)
        sel_scan_odd.append(sel_scan_odd_i)

    return sel_scan_xy, sel_scan_odd