import numpy as np
import numpy.typing as npt

from ..config import Config


def update_select_n (
            sel_n: npt.NDArray[np.float64],
            poses: npt.NDArray[np.float64],
            scans: npt.NDArray[np.float64]
        ):
    '''
    Updates the 2D `ndarray` of occupancy counts `sel_n` in-place according to
    the scan data `scans` collected at each pose in `poses`.

    Parameters:
        sel_n (`ndarray`):
            A 2D `ndarray` occupancy 'hit' values with shape (`h`, `w`), where
            `h` is the height of the occupancy map and `w` is the width of the
            occupancy map.
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        scans (`ndarray`):
            A 3D `ndarray` of sensor data with shape (`n`, `m`, 3), where `n`
            is the number of poses, `m` is the number of beams per pose, local
            `x` values are stored in column 0, local `y` values are stored in
            column 1, and occupancy values are stored in column 2.
    '''

    h, w = sel_n.shape
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

    # Find cell corners
    r_a = np.floor(gy).astype(np.int32)
    c_a = np.floor(gx).astype(np.int32)
    r_b, c_b = r_a + 1, c_a + 1

    # Compute fractional offsets
    dr = gy - r_a
    dc = gx - c_a

    # Compute cell corner weights
    w_a_a = (1 - dr) * (1 - dc)
    w_a_b = (1 - dr) * dc
    w_b_a = dr * (1 - dc)
    w_b_b = dr * dc

    # Concatenate corner indices and weights
    rows = np.concatenate([r_a, r_a, r_b, r_b])
    cols = np.concatenate([c_a, c_b, c_a, c_b])
    weights = np.concatenate([w_a_a, w_a_b, w_b_a, w_b_b])

    # Mask out-of-bounds points
    mask = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    # Flatten indices
    flat_idxs = rows[mask] * w + cols[mask]

    # Count hits
    counts = np.bincount(flat_idxs, weights=weights[mask], minlength=h*w)

    n += counts.reshape(h, w)