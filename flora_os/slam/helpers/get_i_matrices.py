import numpy as np
import numpy.typing as npt
import scipy.sparse as sp


def get_i_matrices (
            odometry: npt.NDArray[np.float64],
            err_s: npt.NDArray[np.float64]
        ) -> tuple[sp.csc_matrix, sp.csc_matrix]:
    '''
    Returns sparse identity matrices derived from the shapes of the incremental
    odometry data in `odometry` and the sensor error data in `err_s`.
    
    Parameters:
        odometry (`ndarray`):
            A 2D `ndarray` of incremental odometry data with shape (`n`, 3),
            where `n` is the number of transitions plus one initial pose value,
            `d_x` values are stored in column 0, `d_y` values are stored in
            column 1, and `d_theta` values are stored in column 2.
        err_s (`ndarray`):
            A 1D `ndarray` of sensor error values with shape (`m`), where `m`
            is the number of sensor measurements.

    Returns:
        i_matrices (`tuple[csc_matrix]`):
            A `tuple` containing two `csc_matrix` sparse identity matrices used
            for weighting error terms for optimization of the gradient descent.

            - **i_o** (`csc_matrix`): The sparse identity matrix for `odometry`
            with shape (3 * (`n`) - 1, 3 * (`n`) - 1), where `n` is the number
            of rows in `odometry`.
            - **i_s** (`csc_matrix`): The sparse identity matrix for `err_s`
            with shape (`m`, `m`), where `m` is the number of values in
            `err_s`.
    '''

    # Create the sparse identity matrix for odometry
    n_o = odometry.shape[0] - 1
    sig_o = np.array([400.0, 400.0, 2500.0])
    diag_sig_o = np.tile(sig_o, (n_o, 1)).reshape(-1)
    i_o = sp.identity(3 * n_o, np.float64, 'csc')
    i_o.setdiag(diag_sig_o)

    # Create the sparse identity matrix for err_s
    i_s = sp.identity(err_s.size, np.float64, 'csc')
    i_s.setdiag(1.0)
    
    return i_o, i_s