import numpy as np
import numpy.typing as npt

from ..config import Config


def update_grid_n (
            grid: npt.NDArray[np.float64],
            poses: npt.NDArray[np.float64],
            scans: npt.NDArray[np.float64]
        ) -> npt.NDArray[np.float64]:
    '''
    Returns a 2D `ndarray` of occupancy counts `n` according to the scan data
    `scans` collected at each pose in `poses`.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
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
        n (`ndarray`):
            A 2D `ndarray` occupancy 'hit' values with shape (`h`, `w`), where
            `h` is the height of the occupancy map and `w` is the width of the
            occupancy map.
    '''

    h, w = grid.shape
    n_poses = poses.shape[0]

    # Reshape scan data
    glob_scans = scans.reshape(-1, 3)
    lx, ly = glob_scans[:, 0], glob_scans[:, 1]

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

    # Convert coordinates to indices
    indices = valid_rows * w + valid_cols

    # Create n
    n = np.bincount(indices, minlength=h*w)

    return n