import numpy as np
import scipy.sparse as sp

from ..config import Config


def select_scan (
            grid: np.ndarray,
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