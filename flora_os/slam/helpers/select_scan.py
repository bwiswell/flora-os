import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from ..config import Config


def select_scan (
            poses: npt.NDArray[np.float64],
            scans: npt.NDArray[np.float64],
            sel_id: npt.NDArray[np.int32]
        ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.int32]]:
    '''
    Returns the subset of scan data with beams that fall within the active
    subset of the occupancy map, as denoted by `sel_id`.

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
        sel_id (`ndarray`):
            A 2D `ndarray` of selection indices with shape (`n`, 2), where `n`
            is the number of selection indices, `i` indices are stored in
            column 0, and `j` indices are stored in column 1. Defaults to
            `None`.

    Returns:
        sel_scan_data (`tuple[ndarray, ndarray]`):
            A `tuple` containing two `ndarray`; the first corresponds to raw
            'beams' of scan data, the second contains indices relating those
            beams to their corresponding poses.

            - **sel_scans** (`ndarray`): A 2D `ndarray` of sensor data with
            shape (`l`, 3), where `l` is the number of sensor 'beams' that fall
            within the selected area, `x` values are stored in column 0, local
            `y` values are stored in column 1, and occupancy values are stored
            in column 2.
            - **pose_idxs** (`ndarray`): A 1D `ndarray` of pose indices with
            shape (`l`), where `l` is the number of sensor 'beams' that fall
            within the selected area.
    '''
    
    h, w = Config.SIZE_I, Config.SIZE_J
    n_poses, m_beams, _ = poses.shape[0]

    # Reshape scan data
    glob_scans = scans.reshape(-1, 3)
    lx, ly = glob_scans[:, 0], glob_scans[:, 1]

    # Get cos(theta) and sin(theta) for all poses for each beam
    pose_idxs = np.repeat(np.arange(n_poses), m_beams)
    thetas = poses[pose_idxs, 2]
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    # Transform scan data into global coordinate space
    gx = (lx * cos_t - ly * sin_t + poses[pose_idxs, 0]) / Config.SCALE
    gy = (lx * sin_t + ly * cos_t + poses[pose_idxs, 1]) / Config.SCALE

    # Create in-bounds mask
    rows = np.floor(gy).astype(np.int32)
    cols = np.floor(gx).astype(np.int32)
    in_bounds = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    # Create lookup mask
    grid_mask = np.zeros(h * w, dtype=bool)
    flat_idxs = sel_id[:, 0] * w + sel_id[:, 1]
    grid_mask[flat_idxs] = True

    # Create hit mask
    hit_mask = np.zeros(n_poses * m_beams, dtype=bool)
    hit_mask[in_bounds] = grid_mask[rows[in_bounds] * w + cols[in_bounds]]

    # Generate 'jagged' output
    sel_scans = glob_scans[hit_mask]
    sel_pose_idxs = pose_idxs[hit_mask]

    return sel_scans, sel_pose_idxs