import numpy as np
import numpy.typing as npt

from ..config import Config


def downsample_scans (
            scans: npt.NDArray[np.float64],
            pose_idxs: npt.NDArray[np.float64],
            config: Config
        ) -> tuple[npt.NDArray, npt.NDArray]:
    '''
    Returns a `tuple` containing two `ndarray`; the first corresponds to sensor
    measurements of scan data, the second contains indices relating those
    measurements to their corresponding poses.

    Parameters:
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
        downsampled (`tuple[ndarray, ndarray]`):
            A `tuple` containing two `ndarray`; the first corresponds to
            downsampled sensor measurements of scan data, the second contains
            indices relating those measurements to their corresponding poses.

            - **low_scans** (`ndarray`): A 2D `ndarray` of sensor data with
            shape (`l`, 3), where `l` is the number of valid (in-bounds)
            downsampled sensor measurements, local `x` values are stored in
            column 0, local `y` values are stored in column 1, and occupancy
            values are stored in column 2.
            - **pose_idxs** (`ndarray`): A 1D `ndarray` of pose indices with
            shape (`l`), where `l` is the number of valid (in-bounds)
            downsampled sensor measurements.
    '''

    # Create free vs. occupied masks
    is_occ = scans[:, 2] > 0
    is_free = ~is_occ

    # Extract occupied points
    occ_scans = scans[is_occ]
    occ_pose_idxs = pose_idxs[is_occ]

    # Extract each n-th free point, where n is the downsampling rate
    free_scans = scans[is_free][::config.down_rate]
    free_pose_idxs = pose_idxs[is_free][::config.down_rate]

    # Combine downsampled data
    low_scans = np.vstack([occ_scans, free_scans])
    low_pose_idxs = np.concatenate([occ_pose_idxs, free_pose_idxs])

    return low_scans, low_pose_idxs