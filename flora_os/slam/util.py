import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from ..util import rotation_matrix, wrap_radians

from .config import Config


def initialize_hh () -> sp.csc_matrix:
    n = ((Config.SIZE_W - 1) * (Config.SIZE_H) * 2 + \
         Config.SIZE_W - 1 + Config.SIZE_H - 1) * 2
    id_i = np.ndarray((n), np.int32)
    id_j = np.ndarray((n), np.int32)
    val = np.ndarray((n), np.int32)
    idx = 0

    for i in range(Config.SIZE_W):
        for j in range(Config.SIZE_H):
            ij_a = Config.SIZE_H * i + j
            ij_b = ij_a + 1
            ij_c = Config.SIZE_H * (i + 1) + j

            if j + 1 < Config.SIZE_H:
                idx += 1
                id_i[idx * 2 - 2] = idx - 1
                id_i[idx * 2 - 1] = idx - 1
                id_j[idx * 2 - 2] = ij_a
                id_j[idx * 2 - 1] = ij_b
                val[idx * 2 - 2] = 1
                val[idx * 2 - 1] = -1

            if i + 1 < Config.SIZE_W:
                idx += 1
                id_i[idx * 2 - 2] = idx - 1
                id_i[idx * 2 - 1] = idx - 1
                id_j[idx * 2 - 2] = ij_a
                id_j[idx * 2 - 1] = ij_c
                val[idx * 2 - 2] = 1
                val[idx * 2 - 1] = -1

    max_id_i = np.max(id_i)
    max_id_j = np.max(id_j)
    j = sp.csc_matrix(
        (val, (id_i, id_j)),
        (max_id_i + 1, max_id_j + 1),
        np.float64
    )
    hh = j.T @ j
    return hh


def poses_to_odometry (poses: np.ndarray) -> np.ndarray:
    odometry = np.zeros_like(poses)
    odometry[0, :] = poses[0, :]
    for i in range(1, poses.shape[0]):
        d_xy = poses[i, 0:2] - poses[i-1, 0:2]
        r_inv = rotation_matrix(poses[i-1, 2]).T
        odometry[i, 0:2] = r_inv @ d_xy
        d_theta = poses[i, 2] - poses[i-1, 2]
        odometry[i, 2] = wrap_radians(d_theta)
    return odometry


def preprocess_scans (
            scans: np.ndarray
        ) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n_beams = scans.shape[1]
    n_poses = scans.shape[0]

    scan_xy: list[np.ndarray] = []
    scan_odd: list[np.ndarray] = []

    for i in range(n_poses):
        total_n_p = int(np.sum(scans[i, :, 1]))
        scan_xy_i = np.ndarray((2, total_n_p), np.float64)
        scan_odd_i = np.ndarray((total_n_p), np.float64)
        n_p_i = 0
        for j in range(n_beams):
            n_p = scans[i, j, 1]
            for k in range(n_p):
                hit_x = scans[i, j, 1] * math.cos(scans[i, j, 0])
                hit_y = scans[i, j, 1] * math.sin(scans[i, j, 0])
                if k == 0:
                    scan_xy_i[0, n_p_i] = hit_x
                    scan_xy_i[1, n_p_i] = hit_y
                    scan_odd_i[n_p_i] = Config.OCCUPIED
                else:
                    scan_xy_i[0, n_p_i + k] = (hit_x / n_p) * (n_p - k)
                    scan_xy_i[1, n_p_i + k] = (hit_y / n_p) * (n_p - k)
                    scan_odd_i[n_p_i + k] = Config.FREE
            n_p_i += n_p
        scan_xy.append(scan_xy_i)
        scan_odd.append(scan_odd_i)

    return scan_xy, scan_odd