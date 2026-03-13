import numpy as np
import numpy.typing as npt

from ..config import Config

from .rotate_and_scale import rotate_and_scale


def update_grid_n (
            poses: npt.NDArray[np.float64],
            scan_xy: list[npt.NDArray[np.float64]]
        ) -> npt.NDArray[np.float64]:
    '''
    Returns a 2D `ndarray` of occupancy counts `n` according to the scan data
    `scan_xy` collected at each pose in `poses`.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        scan_xy (`list[ndarray]`):
            a `list` of length `n` of 2D `ndarray` of `xy`-coordinates with
            shapes (2, `m`), where `n` is the number of poses scan data was
            collected from (should match `poses`), `m` is the number of scan
            angles collected at each pose, `x` values are stored in row 0, and
            `y` values are stored in row 1.

    Returns:
        n (`ndarray`):
            A 2D `ndarray` occupancy 'hit' values with shape (`h`, `w`), where
            `h` is the height of the occupancy map and `w` is the width of the
            occupancy map.
    '''
    
    # Create rotation matrices for all poses
    cos_theta = np.cos(poses[:, 2])
    sin_theta = np.sin(poses[:, 2])
    r = np.stack(
        [
            np.stack([cos_theta, -sin_theta], axis=1),
            np.stack([sin_theta, cos_theta], axis=1)
        ],
        axis = 1
    )

    # Transform xy-coordinates
    xy = np.hstack([
        r[i] @ scan_xy[i] + poses[i, :2, np.newaxis]
        for i in range(len(scan_xy))
    ])

    # Scale and round coordinates
    xy = np.round(xy / Config.SCALE).astype(np.int32)

    # Create histogram of 'hits' in n
    n = np.zeros((Config.SIZE_I, Config.SIZE_J), np.float64)
    np.add.at(n, (xy[0], xy[1]), 1)

    return n