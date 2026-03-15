import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from ..config import Config


def select_initial_grid (
            poses: npt.NDArray[np.float64],
            sel_scans: npt.NDArray[np.float64],
            pose_idxs: npt.NDArray[np.int32],
            config: Config
        ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    '''
    Returns `tuple` of two 2D `ndarray` containing the initial occupancy map
    for the selected subset of scan data and the initial 'hit' count for the
    same, respectively.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        sel_scans (`ndarray`): A 2D `ndarray` of sensor data with shape
            (`l`, 3), where `l` is the number of sensor 'beams' that fall
            within the selected area, `x` values are stored in column 0, local
            `y` values are stored in column 1, and occupancy values are stored
            in column 2.
        pose_idxs (`ndarray`): A 1D `ndarray` of pose indices with shape (`l`),
            where `l` is the number of sensor 'beams' that fall within the
            selected area.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        initial_grid (`tuple[ndarray, ndarray]`):
            A `tuple` of two 2D `ndarray` containing the initial occupancy map
            for the selected subset of scan data and the initial 'hit' count
            for the same, respectively, each with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.

            - **grid** (`ndarray`): A 2D `ndarray` containing the initial
            occupancy map.
            - **n** (`ndarray`): A 2D `ndarray` containing the initial 'hit'
            count map.
    '''

    h, w = config.size_i, config.size_j

    # Reshape scan data
    lx, ly, obs = sel_scans[:, 0], sel_scans[:, 1], sel_scans[:, 2]

    # Get cos(theta) and sin(theta) for all poses for each beam
    thetas = poses[pose_idxs, 2]
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    # Transform scan data into global coordinate space
    gx = (lx * cos_t - ly * sin_t + poses[pose_idxs, 0]) / config.scale
    gy = (lx * sin_t + ly * cos_t + poses[pose_idxs, 1]) / config.scale

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

    # Concatenate corner indices
    rows = np.concatenate([r_a, r_a, r_b, r_b])
    cols = np.concatenate([c_a, c_b, c_a, c_b])

    # Compute grid/n vals
    grid_vals = np.concatenate([
        w_a_a * obs,
        w_a_b * obs,
        w_b_a * obs,
        w_b_b * obs
    ])
    n_vals = np.concatenate([w_a_a, w_a_b, w_b_a, w_b_b])

    # Mask out-of-bounds points
    mask = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)

    # Flatten indices
    flat_idxs = rows[mask] * w + cols[mask]

    # Count hits
    grid = np.bincount(flat_idxs, weights=grid_vals[mask], minlength=h*w)
    n = np.bincount(flat_idxs, weights=n_vals[mask], minlength=h*w)

    return grid.reshape(h, w), n.reshape(h, w)