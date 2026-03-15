import numpy as np
import numpy.typing as npt

from ..config import Config


def initialize_grid_map (
            poses: npt.NDArray[np.float64],
            scans: npt.NDArray[np.float64],
            pose_idxs: npt.NDArray[np.int32],
            config: Config
        ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    '''
    Returns a `tuple` of `ndarray` containing the initialized occupancy map and
    occupancy 'hit' count matrix `n`.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        scans (`ndarray`):
            A 2D `ndarray` of sensor data with shape (`l`, 3), where `l` is the
            number of valid (in-bounds) sensor measurements, local `x` values
            are stored in column 0, local `y` values are stored in column 1,
            and occupancy values are stored in column 2.
        pose_idxs (`ndarray`):
            A 1D `ndarray` of pose indices with shape (`l`), where `l` is the
            number of valid (in-bounds) sensor measurements.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        grid_data (`tuple[ndarray, ndarray]`):
            A `tuple` of two 2D `ndarray` containing the initialized occupancy
            map and occupancy 'hit' count matrix `n`, each with shape
            (`h`, `w`), where `h` is the map height and `w` is the map width.

            - **grid** (`ndarray`): The initial occupancy map.
            - **n** (`ndarray`): The initial occupancy 'hit' count matrix.
    '''

    h, w = config.size_i, config.size_j
    n_poses = poses.shape[0]

    # Reshape scan data
    lx, ly = scans[:, 0], scans[:, 1]
    glob_obs = scans[:, 2]

    # Get cos(theta) and sin(theta) for all poses for each beam
    thetas = poses[pose_idxs, 2]
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    # Transform scan data into global coordinate space
    gx = (lx * cos_t - ly * sin_t + poses[pose_idxs, 0]) / config.scale
    gy = (lx * sin_t + ly * cos_t + poses[pose_idxs, 1]) / config.scale

    # Floor and cast scan data
    rows = np.floor(gy).astype(np.int32)
    cols = np.floor(gx).astype(np.int32)

    # Mask out-of-bounds points
    mask = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)
    valid_rows = rows[mask]
    valid_cols = cols[mask]
    valid_obs = glob_obs[mask]

    # Convert coordinates to indices
    indices = valid_rows * w + valid_cols

    # Create grid and n
    grid = np.bincount(indices, weights=valid_obs, minlength=h*w)
    n = np.bincount(indices, minlength=h*w).astype(np.float64)

    return grid.reshape(h, w), n.reshape(h, w)