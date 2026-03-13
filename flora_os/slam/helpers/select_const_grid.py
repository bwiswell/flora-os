import numpy as np
import scipy.sparse as sp

from ..config import Config


def select_const_grid (sel_id_var: np.ndarray) -> sp.csc_matrix:
    rows = sel_id_var[:, 0]
    cols = sel_id_var[:, 1]

    flat_ids = rows * Config.SIZE_H + cols
    ids = np.sort(flat_ids)
    n_vars = len(ids)

    ids_right = rows * Config.SIZE_H + (cols + 1)
    ids_below = (rows + 1) * Config.SIZE_H + cols

    def get_neighbor_indices (targ_ids: np.ndarray):
        indices = np.searchsorted(ids, targ_ids)
        mask = (indices < n_vars) & (ids[indices] == targ_ids)
        return indices, mask
    
    ids_right, mask_right = get_neighbor_indices(ids_right)
    ids_below, mask_below = get_neighbor_indices(ids_below)

    n_r = np.sum(mask_right)
    n_b = np.sum(mask_below)
    n_const = n_r + n_b

    j_rows = np.repeat(np.arange(n_const), 2)
    j_cols = np.zeros(2 * n_const, dtype=np.int32)
    j_vals = np.tile([1.0, -1.0], n_const)

    valid_r = np.where(mask_right)[0]
    ids_self, _ = get_neighbor_indices(flat_ids)

    j_cols[0:2*n_r:2] = ids_self[mask_right]
    j_cols[1:2*n_r:2] = ids_right[mask_right]
    j_cols[2*n_r::2] = ids_self[mask_below]
    j_cols[2*n_r+1::2] = ids_below[mask_below]

    j = sp.csc_matrix((j_vals, (j_rows, j_cols)), shape=(n_const, n_vars))

    return j.T @ j