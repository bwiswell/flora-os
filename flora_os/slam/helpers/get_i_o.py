import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from ..config import Config


def get_i_o (
            odometry: npt.NDArray[np.float64],
            config: Config
        ) -> sp.csc_matrix:
    '''
    Returns a sparse identity matrix derived from the shapes of the incremental
    odometry data in `odometry` and the error weights in `Config`.
    
    Parameters:
        odometry (`ndarray`):
            A 2D `ndarray` of incremental odometry data with shape
            (`n`, 3), where `n` is the number of poses, `d_x` values are stored
            in column 0, `d_y` values are stored in column 1, and `d_theta`
            values are stored in column 2.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        i_o (`csc_matrix`): The sparse identity matrix for `odometry` with
        shape (3 * (`n` - 1), 3 * (`n` - 1)), where `n` is the number of rows
        in `odometry`.
    '''

    # Create the sparse identity matrix for odometry
    n_o = odometry.shape[0] - 1
    sig_o = np.array(
        [config.weight_xy, config.weight_xy, config.weight_theta],
        np.float64
    )
    diag_sig_o = np.tile(sig_o, n_o)
    i_o = sp.diags(diag_sig_o, format='csc')
    
    return i_o