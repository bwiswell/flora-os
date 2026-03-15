import numpy as np
import numpy.typing as npt

from ..config import Config


def initialize_odometry (
            imu_poses: npt.NDArray[np.float64],
            config: Config
        ) -> npt.NDArray[np.float64]:
    '''
    Returns a `tuple` of two 2D 'ndarray' containing odometry 'increment'
    measurements derived from the global coordinate system pose 'estimates' in
    `imu_poses` taken from IMU and a 'shifted' set of pose estimates (to avoid
    negative coordinates) respectively.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        positioning_data (`tuple[ndarray, ndarray]`):
            A `tuple` of two 2D 'ndarray' containing odometry 'increment'
            measurements derived from the global coordinate system pose
            'estimates' in `imu_poses` taken from IMU and a 'shifted' set of
            pose estimates (to avoid negative coordinates) respectively, each
            with shape (`n`, 3), where `n` is the number of poses, `x` values
            are stored in column 0, `y` values are stored in column 1, and
            `theta` values are stored in column 2.

            - **odometry** (`ndarray`): A 2D `ndarray` of incremental odometry
            data.
            - **poses** (`ndarray`): A 2D `ndarray` of poses.
    '''

    n_poses = imu_poses.shape[0]
    poses = imu_poses.copy()

    # Offset the initial pose estimates to avoid negative coordinates
    poses[:, 0] += (config.size_j * config.scale) / 2
    poses[:, 1] += (config.size_i * config.scale) / 2

    # Initialize the odometry ndarray
    odometry = np.zeros_like(poses)

    # Check that there are enough poses to justify calculating increments
    if n_poses < 2:
        return odometry, poses
    
    # Calculate global displacements
    d_gx = np.diff(poses[:, 0])
    d_gy = np.diff(poses[:, 1])
    d_gt = (np.diff(poses[:, 2]) + np.pi) % (2 * np.pi) - np.pi

    # Translate global coordinates into local coordinates
    prev_theta = poses[:-1, 2]
    cos_t = np.cos(prev_theta)
    sin_t = np.sin(prev_theta)
    d_lx = d_gx * cos_t + d_gy * sin_t
    d_ly = -d_gx * sin_t + d_gy * cos_t

    odometry[1:, 0] = d_lx
    odometry[1:, 1] = d_ly
    odometry[1:, 2] = d_gt

    return odometry, poses