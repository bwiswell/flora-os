import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def smooth_n2 (n: np.ndarray, hh: sp.csc_matrix) -> np.ndarray:
    rows, cols = np.nonzero(n)
    vals = n[rows, cols]
    n_nz = rows.shape[0]

    id_i = np.arange(n_nz)
    id_j = rows * Config.SIZE_H + cols
    a = sp.csc_matrix(
        (np.ones((n_nz)), (id_i, id_j)),
        (n_nz, Config.SIZE_W * Config.SIZE_H),
        np.float64
    )

    ii = a.T @ a + hh * Config.WEIGHT_SMOOTH_N
    ee = a.T * vals

    solve = spl.splu(ii.tocsc())
    delta_n: np.ndarray = solve(ee)

    return delta_n.reshape((Config.SIZE_W, Config.SIZE_H))