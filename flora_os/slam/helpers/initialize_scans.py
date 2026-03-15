import numpy as np
import numpy.typing as npt

from ..config import Config


def initialize_scans (
            sonar: npt.NDArray[np.float64],
            config: Config
        ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.int32]]:
    '''
    Returns a `tuple` containing two `ndarray`; the first corresponds to raw
    'beams' of scan data, the second contains indices relating those beams to
    their corresponding poses.

    Parameters:
        sonar (`ndarray`):
            A 2D `ndarray` containing raw sonar sensor data with shape
            (`n`, 'm', 2), where 'n' is the number of poses, 'm' is the number
            of sonar beams per pose, 'theta' values are stored in column 0, and
            'dist' values are stored in column 1.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        scan_data (`tuple[ndarray, ndarray]`):
            A `tuple` containing two `ndarray`; the first corresponds to raw
            'beams' of scan data, the second contains indices relating those
            beams to their corresponding poses.

            - **scans** (`ndarray`): A 2D `ndarray` of sensor data with shape
            (`l`, 3), where `l` is the total number of 'valid' sensor beams,
            local `x` values are stored in column 0, local `y` values are
            stored in column 1, and occupancy values are stored in column 2.
            - **pose_idxs** (`ndarray`): A 1D `ndarray` of pose indices with
            shape (`l`), where `l` is the total number of 'valid' sensor beams.
        
    '''
    
    n_poses, n_beams, _ = sonar.shape

    # Reshape sonar and create beam to pose mapping
    flat_scans = sonar.reshape(-1, 2)
    beam_pose_idxs = np.repeat(np.arange(n_poses), n_beams)

    # Filter for invalid/dead-zone readings
    valid_mask = flat_scans[:, 1] > 0
    angles = flat_scans[valid_mask, 0]
    dists = flat_scans[valid_mask, 1]
    pose_idxs = beam_pose_idxs[valid_mask]

    # Check if there are no valid scans
    if len(dists) == 0:
        return np.empty((0, 3)), np.empty(0, dtype=np.int32)
    
    # Calculate number of samples per beam
    n_samples = (dists / config.scale).astype(np.int32)
    max_samples = np.max(n_samples)

    # Create ramp and mask for handling varying beam lengths
    ramp = np.linspace(0, 1, max_samples, endpoint=False)
    mask = np.arange(max_samples) < n_samples[:, None]

    # Project free points radially
    cos_t = np.cos(angles)
    sin_t = np.sin(angles)
    free_x = (dists[:, None] * cos_t[:, None]) * ramp
    free_y = (dists[:, None] * sin_t[:, None]) * ramp

    # Create free point to pose mapping
    free_pose_idx = np.repeat(
        pose_idxs,
        max_samples
    ).reshape(len(pose_idxs), max_samples)[mask]

    # Create free point cloud
    free_points = np.column_stack([
        free_x[mask],
        free_y[mask],
        np.full(free_x.size, Config.FREE)
    ])

    # Find 'hits' in sonar data
    is_hit = dists < Config.MAX_RANGE_M_SONAR
    hit_angles = angles[is_hit]
    hit_dists = dists[is_hit]
    hit_pose_idxs = pose_idxs[is_hit]

    # 'Hit' arc offsets
    offsets = np.array([-Config.CONE_HALF_WIDTH, 0.0, Config.CONE_HALF_WIDTH])

    # Create the expanded 'hit' arcs
    exp_angles = hit_angles[:, None] + offsets
    exp_dists = hit_dists[:, None]
    occ_x = (exp_dists * np.cos(exp_angles)).ravel()
    occ_y = (exp_dists * np.sin(exp_angles)).ravel()

    # Create 'hit' arc occupancy values with probabilistic smoothing
    occ_vals = np.tile(
        [Config.OCCUPIED * 0.5, Config.OCCUPIED, Config.OCCUPIED * 0.5],
        len(hit_angles)
    )
    occ_pose_idxs = np.repeat(hit_pose_idxs, 3)

    # Create occupied point cloud
    occ_points = np.column_stack([occ_x, occ_y, occ_vals])

    # Aggregate point clouds
    scans = np.vstack([free_points, occ_points])
    pose_idxs = np.concatenate([free_pose_idx, occ_pose_idxs])

    return scans, pose_idxs