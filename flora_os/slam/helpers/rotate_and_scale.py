import numpy as np

from ..config import Config

from .util import rotation_matrix


def rotate_and_scale (
            pose: np.ndarray,
            scan_xy_i: np.ndarray
        ) -> tuple[np.ndarray, np.ndarray]:
    r_i = rotation_matrix(pose[2])
    scan_xy_i_mat = scan_xy_i.reshape((2, -1), order='F')
    pose_vec = pose[:2].T
    s_i = (r_i @ scan_xy_i_mat) + pose_vec
    xy = (s_i / Config.SCALE).round().astype(np.int32)
    return scan_xy_i_mat, xy