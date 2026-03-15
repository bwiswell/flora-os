from typing import Optional

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def smooth_n2 (
            n: npt.NDArray[np.float64],
            weighted_hh: sp.csc_matrix,
            config: Config,
            sel_id_var: Optional[npt.NDArray[np.int32]] = None
        ) -> npt.NDArray[np.float64]:
    '''
    Returns a 'smoothed' version of `n` according to the Hessian `hh`. If
    `sel_id_var`, smoothes the entire map. Otherwise, smooths only for the
    selection indices.

    Parameters:
        n (`ndarray`):
            A 2D `ndarray` of occupancy 'hit' values with shape (`h`, `w`), where
            `h` is the height of the occupancy map and `w` is the width of the
            occupancy map.
        weighted_hh (`csc_matrix`):
            A `csc_matrix` containing a weighted Hessian with shape
            (`w` * `h`, `w` * `h`), where `w` is the map width and `h` is the
            map height.
        config (`Config`):
            The configuration object to obtain setting selection values from.
        sel_id_var (`Optional[ndarray]`):
            A 2D `ndarray` of selection indices with shape (`n`, 2), where `n`
            is the number of selection indices, `i` indices are stored in
            column 0, and `j` indices are stored in column 1. Defaults to
            `None`.

    Returns:
        smoothed_n (`ndarray`):
            A 2D `ndarray` of smoothed occupancy 'hit' values with shape
            (`h`, `w`), where `h` is the height of the occupancy map and `w` is
            the width of the occupancy map.
    '''

    h, w = n.shape
    n_flat = n.ravel()

    # Determine the active space and create the observation diagonal
    if sel_id_var is not None:
        active_indices = np.sort(sel_id_var[:, 0] * w + sel_id_var[:, 1])
        b_vec = n_flat[active_indices]
    else:
        b_vec = n_flat
    diag_val = (b_vec > 0).astype(np.float64)

    # Build ii and ee
    ii = sp.diags(diag_val, format='csc') + weighted_hh

    # Create Jacobi preconditioner
    m_inv = sp.diags(1.0 / np.maximum(ii.diagonal(), 1e-6))

    # Solve the system with the Conjugate Gradient method
    params = config.smooth_solver_params(
        sel_id_var is not None,
        len(active_indices) if sel_id_var is not None else n.size
    )
    delta_active, _ = spl.cg(ii, b_vec, M=m_inv, **params)

    # Update the full grid
    if sel_id_var is not None:
        smoothed_n = np.zeros(n.size, dtype=np.float64)
        smoothed_n[active_indices] = delta_active
    else:
        smoothed_n = delta_active

    return smoothed_n