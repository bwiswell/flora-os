import numpy as np
import scipy.sparse as sp

from ..config import Config

from .bilinear_interpolation import bilinear_interpolation
from .compute_jo import compute_jo


def diff_jacobian (
            grid: np.ndarray,
            n: np.ndarray,
            poses: np.ndarray,
            odometry: np.ndarray,
            scans: np.ndarray,
            config: Config
        ) -> tuple[
            sp.csc_matrix,
            sp.csc_matrix,
            sp.csc_matrix,
            np.ndarray,
            np.ndarray
        ]:
    '''
    Returns `tuple` of 3 `csc_matrix` and 2 `ndarray`, containing the pose
    Jacobian, grid (disparity) Jacobian, odometry Jacobian, sensor residual
    errors, and odometry residual errors respectively.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
        n (`ndarray`):
            A 2D `ndarray` of occupancy 'hit' values with shape (`h`, `w`),
            where `h` is the height of the occupancy map and `w` is the width
            of the occupancy map.
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        odometry (`ndarray`):
            A 2D `ndarray` of incremental odometry data with shape
            (`n`, 3), where `n` is the number of poses, `d_x` values are stored
            in column 0, `d_y` values are stored in column 1, and `d_theta`
            values are stored in column 2.
        scans (`ndarray`):
            A 3D `ndarray` of sensor data with shape (`n`, `m`, 3), where `n`
            is the number of poses, `m` is the number of beams per pose, local
            `x` values are stored in column 0, local `y` values are stored in
            column 1, and occupancy values are stored in column 2.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        js (`tuple[csc_matrix, csc_matrix, csc_matrx, ndarray, ndarray`]):
            A `tuple` of 3 `csc_matrix` and 2 `ndarray`, containing the pose
            Jacobian, grid (disparity) Jacobian, odometry Jacobian, sensor
            residual errors, and odometry residual errors respectively.

            - **jp** (`csc_matrix`): A `csc_matrix` containing the pose
            Jacobian with shape (`l`, 3 * `n`), where `l` is the number of
            valid (in-bounds) sensor measurements and `n` is the number poses.
            - **jd** (`csc_matrix`): A `csc_matrix` containing the grid
            (disparity) Jacobian with shape (`l`, `w` * `h`), where `l` is the
            number of valid (in-bounds) sensor measurements, `w` is the map
            width, and `h` is the map height.
            - **jo** (`csc_matrix`): A `csc_matrix` containing the odometry
            Jacobian with shape (3 * (`n` - 1), 3 * `n`)
    '''
    
    n_poses = poses.shape[0]
    n_beams = scans.shape[1]

    # Compute spatial gradients
    gv, gu = np.gradient(grid, config.scale)

    # Reshape scan data
    glob_scans = scans.reshape(-1, 3)
    lx, ly = glob_scans[:, 0], glob_scans[:, 1]
    glob_obs = glob_scans[:, 2]

    # Get cos(theta) and sin(theta) for all poses for each beam
    pose_idxs = np.repeat(np.arange(n_poses), n_beams)
    thetas = poses[pose_idxs, 2]
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    # Transform scan data into global coordinate space
    gx = (lx * cos_t - ly * sin_t + poses[pose_idxs, 0]) / config.scale
    gy = (lx * sin_t + ly * cos_t + poses[pose_idxs, 1]) / config.scale
    xy = np.stack([gx, gy], axis=1)

    # Global bilinear interpolation
    m_v, mask, idxs, weights = bilinear_interpolation(grid, xy)
    n_v, _, _, _ = bilinear_interpolation(n, xy)

    # Gradient bilinear interpolation
    gu_v, _, _, _ = bilinear_interpolation(gu, xy)
    gv_v, _, _, _ = bilinear_interpolation(gv, xy)

    # Filter and invert n results
    n_safe = np.where(n_v[mask] == 0, 1.0, n_v[mask])
    inv_n = 1.0 / (n_safe * config.scale)

    # Compute residual sensor error
    err_s = m_v[mask] / n_safe - glob_obs[mask]
    n_valid = err_s.size

    # Build pose Jacobian translation and rotation components
    dm_dx = gu_v[mask] * inv_n
    dm_dy = gv_v[mask] * inv_n
    dgx_dt = (-lx[mask] * sin_t[mask] - ly[mask] * cos_t[mask]) / config.scale
    dgy_dt = (lx[mask] * cos_t[mask] - ly[mask] * sin_t[mask]) / config.scale
    dm_dt = (gu_v[mask] * dgx_dt + gv_v[mask] * dgy_dt) * inv_n

    # Assemble pose Jacobian
    rows = np.arange(n_valid)
    valid_pose_idxs = pose_idxs[mask]
    jp_i = np.tile(rows, 3)
    jp_j = np.concatenate([
        3 * valid_pose_idxs,
        3 * valid_pose_idxs + 1,
        3 * valid_pose_idxs + 2
    ])
    jp_v = np.concatenate([dm_dx, dm_dy, dm_dt])
    jp = sp.csc_matrix((jp_v, (jp_i, jp_j)), shape=(n_valid, 3 * n_poses))

    # Assemble disparity Jacobian
    jd_i = np.tile(rows, 4)
    jd_j = idxs.ravel()
    jd_v = (weights * inv_n).ravel()
    jd = sp.csc_matrix((jd_v, (jd_i, jd_j)), shape=(n_valid, grid.size))

    # Get odometry Jacobian
    err_o, jo = compute_jo(poses, odometry)

    return jp, jd, jo, err_s, err_o