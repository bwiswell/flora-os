import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def smooth_n2 (n: np.ndarray, hh: sp.csc_matrix) -> np.ndarray:
    rows, cols = np.nonzero(n)
    vals = n[rows, cols]
    n_nz = rows.shape[0]
    id_i = np.array(list(range(n_nz)), np.int32)
    id_j = rows * Config.SIZE_H + cols
    np_ones = np.ones((n_nz))
    ones = sp.csc_matrix(
        (np_ones, (id_i, id_j)),
        (n_nz, Config.SIZE_W * Config.SIZE_H),
        np.float64
    )
    ii = ones.T @ ones + hh
    ee = ones.T * vals
    solve = spl.factorized(ii)
    delta_n: np.ndarray = solve(ee)
    return delta_n.reshape((Config.SIZE_H, Config.SIZE_W)).T