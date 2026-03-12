import numpy as np
import scipy.sparse as sp


def get_i_matrices (
            odometry: np.ndarray,
            err_s: np.ndarray
        ) -> tuple[sp.csc_matrix, sp.csc_matrix]:
    i_s = sp.identity(err_s.size, np.float64, 'csc')
    i_s.setdiag(1.0)
    n_o = odometry.shape[0] - 1
    sig_o = np.array([400.0, 400.0, 2500.0])
    diag_sig_o = np.tile(sig_o, (n_o, 1)).reshape(-1)
    i_o = sp.identity(3 * n_o, np.float64, 'csc')
    i_o.setdiag(diag_sig_o)
    return i_s, i_o