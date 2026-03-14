import numpy as np

from ..config import Config


def initialize_grid_map (
            poses: np.ndarray,
            scans: np.ndarray
        ) -> tuple[np.ndarray, np.ndarray]:
    '''
    Returns a `tuple` of `ndarray` containing the initialized occupancy map and
    occupancy 'hit' count matrix `n`.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        scans (`ndarray`):
            A 3D `ndarray` of sensor data with shape (`n`, `m`, 3), where `n`
            is the number of poses, `m` is the number of beams per pose, local
            `x` values are stored in column 0, local `y` values are stored in
            column 1, and occupancy values are stored in column 2.

    Returns:
        grid_data (`tuple[ndarray, ndarray]`):
            A `tuple` of two 2D `ndarray` containing the initialized occupancy
            map and occupancy 'hit' count matrix `n`, each with shape
            (`h`, `w`), where `h` is the map height and `w` is the map width.

            - **grid** (`ndarray`): The initial occupancy map.
            - **n** (`ndarray`): The initial occupancy 'hit' count matrix.
    '''

    h, w = Config.SIZE_I, Config.SIZE_J
    n_poses = poses.shape[0]

    # Reshape scan data
    glob_scans = scans.reshape(-1, 3)
    lx, ly = glob_scans[:, 0], glob_scans[:, 1]
    glob_obs = glob_scans[:, 2]

    # Get cos(theta) and sin(theta) for all poses for each beam
    pose_idxs = np.repeat(np.arange(n_poses), Config.N_BEAMS)
    thetas = poses[pose_idxs, 2]
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    # Transform scan data into global coordinate space
    gx = (lx * cos_t - ly * sin_t + poses[pose_idxs, 0]) / Config.SCALE
    gy = (lx * sin_t + ly * cos_t + poses[pose_idxs, 1]) / Config.SCALE

    # Clip and cast scan data
    rows = np.rint(gy).astype(np.int32)
    cols = np.rint(gx).astype(np.int32)

    # Mask out-of-bounds points
    mask = (rows >= 0) and (rows < h) and (cols >= 0) and (cols < w)
    valid_rows = rows[mask]
    valid_cols = cols[mask]
    valid_obs = glob_obs[mask]

    # Convert coordinates to indices
    indices = valid_rows * w + valid_cols

    # Create grid and n
    grid = np.bincount(indices, weights=valid_obs, minlength=h*w)
    n = np.bincount(indices, minlength=h*w)

    return grid.reshape(h, w), n.reshape(h, w).astype(np.float64)