import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from ..config import Config


def select_laplacian (sel_id_var: npt.NDArray[np.int32]) -> sp.csc_matrix:
    '''
    Returns a weighted Laplacian smoothing matrix for the active subset of the
    grid defined by `sel_id_var`.

    Parameters:
        sel_id_var (`ndarray`):
            A 2D `ndarray` of selection indices with shape (`n`, 2), where `n`
            is the number of selection indices, `i` indices are stored in
            column 0, and `j` indices are stored in column 1.

    Returns:
        laplacian (`csc_matrix`):
            A `csc_matrix` containing the weighted Laplacian with shape
            (`n`, `n`), where `n` is the number of selection indices.
    '''

    h, w = Config.SIZE_I, Config.SIZE_J

    # Extract index values
    rows = sel_id_var[:, 0]
    cols = sel_id_var[:, 1]

    # Flatten and sort indices
    flat_ids = rows * h + cols
    ids = np.sort(flat_ids)
    n_vars = len(ids)

    # Get self-referential indices
    ids_self = np.searchsorted(ids, flat_ids)

    # Get neighbor target indices
    ids_right = rows * h + (cols + 1)
    ids_below = (rows + 1) * h + cols

    def get_neighbor_indices (targ_ids: np.ndarray):
        '''Finds neighbor indices that are part of the active subset.'''
        idxs = np.searchsorted(ids, targ_ids)
        mask = (idxs < n_vars) & \
                (ids[idxs == np.clip(idxs, 0, n_vars - 1)] == targ_ids)
        return idxs, mask
    
    ids_right, mask_right = get_neighbor_indices(ids_right)
    ids_below, mask_below = get_neighbor_indices(ids_below)

    # Build Jacobian values
    n_r = np.sum(mask_right)
    n_b = np.sum(mask_below)
    n_const = n_r + n_b

    # Build Jacobian components
    j_rows = np.repeat(np.arange(n_const), 2)
    j_cols = np.zeros(2 * n_const, dtype=np.int32)
    j_vals = np.tile([1.0, -1.0], n_const)

    # Fill right and below neighbor constraints
    j_cols[0:2*n_r:2] = ids_self[mask_right]
    j_cols[1:2*n_r:2] = ids_right[mask_right]
    j_cols[2*n_r::2] = ids_self[mask_below]
    j_cols[2*n_r+1::2] = ids_below[mask_below]

    # Build the Jacobian matrix
    j = sp.csc_matrix((j_vals, (j_rows, j_cols)), shape=(n_const, n_vars))

    # Get the Laplacian
    l = (j.T @ j) * Config.MAP_SMOOTHING_WEIGHT_SECOND

    return l.tocsc()