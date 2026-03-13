import numpy as np
import numpy.typing as npt


def update_grid (
            grid: npt.NDArray[np.float64],
            poses: npt.NDArray[np.float64],
            delta_d: npt.NDArray[np.float64],
            delta_p: npt.NDArray[np.float64]
        ):
    '''
    Updates the occupancy map `grid` and pose array `poses` in place using the
    gradient `delta_p` and `delta_d` values obtained from the `delta` helper
    method.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map width and `w` is the map height.
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        delta_d (`ndarray`):
            A 2D `ndarray` of occupancy map gradient deltas with shape
            (`n`, 1), where `n` is equal to `grid.size`.
        delta_p (`ndarray`):
            A 2D `ndarray` of pose gradient deltas with shape (`n`, 1), where
            `n` is equal to `poses.size`.
    '''
    delta_d_mat = delta_d.reshape(grid.shape, order='F')
    grid += delta_d_mat
    delta_p_mat = delta_p.reshape((-1, 3), order='F')
    poses[1:, :] += delta_p_mat