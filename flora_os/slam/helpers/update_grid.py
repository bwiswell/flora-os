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
            is the map height and `w` is the map width.
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        delta_d (`ndarray`):
            A 1D `ndarray` of occupancy map parameter deltas with shape
            (`w` * `h`), where `w` is the map width and `h` is the map height.
        delta_p (`ndarray`):
            A 1D `ndarray` of pose parameter deltas with shape (3 * `n` - 3),
            where `n` is the number of poses.
    '''

    # Apply gradient delta update to the occupancy map
    grid += delta_d.reshape(grid.shape)

    # Apply gradient delta update to the pose array
    poses[1:, :] += delta_p.reshape((-1, 3))
    poses[:, 2] = (poses[:, 2] + np.pi) % (2 * np.pi) - np.pi