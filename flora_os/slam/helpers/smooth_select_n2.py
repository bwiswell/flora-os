import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def smooth_select_n2 (
            sel_n: np.ndarray,
            sel_weighted_hh: sp.csc_matrix,
            sel_id_var: np.ndarray
        ) -> np.ndarray:
    rows, cols = np.nonzero(sel_n)
    vals = sel_n[rows, cols]
    n_nz = rows.shape[0]

    id_i = np.arange(n_nz)
    id_j = rows * Config.SIZE_H + cols
    a = sp.csc_matrix(
        (np.ones((n_nz)), (id_i, id_j)),
        (n_nz, Config.SIZE_W * Config.SIZE_H),
        np.float64
    )

    sorted_ids = np.sort(sel_id_var[:, 0] * Config.SIZE_H + sel_id_var[:, 1])
    sel_a = a[:, sorted_ids]

    ii = (sel_a.T @ sel_a) + sel_weighted_hh
    ee = sel_a.T @ vals

    sel_delta_n, _ = spl.cg(
        ii, ee,
        tol = Config.SOLVER_TOLERANCE_SECOND,
        atol = 'legacy'
    )

    delta_n = np.zeros(Config.SIZE_W * Config.SIZE_H, np.float64)
    delta_n[sorted_ids] = sel_delta_n
    return delta_n.reshape((Config.SIZE_W, Config.SIZE_H))