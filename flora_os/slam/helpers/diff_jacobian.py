import numpy as np
import scipy.sparse as sp

from ..config import Config

from .bilinear_interpolation import bilinear_interpolation
from .util import d_rotation_matrix, rotation_matrix, wrap_radians
from .get_i_matrices import get_i_matrices
from .gradient import gradient


def diff_jacobian (
            grid: np.ndarray,
            n: np.ndarray,
            poses: np.ndarray,
            odometry: np.ndarray,
            scan_xy: list[np.ndarray],
            scan_odd: list[np.ndarray]
        ) -> tuple[
            sp.csc_matrix,
            sp.csc_matrix,
            sp.csc_matrix,
            sp.csc_matrix,
            sp.csc_matrix,
            np.ndarray,
            np.ndarray
        ]:
    n_poses = poses.shape[0]
    h = 1.0
    g_v, g_u = gradient(grid, h)
    n_pts = 0

    jp_id_i, jp_id_j, jp_val = [], [], []
    jd_id_i, jd_id_j, jd_val = [], [], []
    jo_id_i, jo_id_j, jo_val = [], [], []
    err_s, err_o = [], []

    for i in range(n_poses):
        scan_xy_i = scan_xy[i]
        scan_odd_i = scan_odd[i]

        theta = poses[i, 2]
        r_i = rotation_matrix(theta)
        scan_xy_i_mat = scan_xy_i.reshape((2, -1), order='F')
        pose_vec = poses[i, :2].T
        s_i = (r_i @ scan_xy_i_mat) + pose_vec
        xy = (s_i / Config.SCALE).round().astype(np.int32)

        grid_inter = bilinear_interpolation(grid, xy.T)
        n_inter = bilinear_interpolation(n, xy.T)

        err_s.append(grid_inter / n_inter - scan_odd_i)

        g_u_inter = bilinear_interpolation(g_u, xy.T)
        g_v_inter = bilinear_interpolation(g_v, xy.T)

        d_m_d_xy = np.vstack([g_u_inter / n_inter, g_v_inter / n_inter])
        d_r_i = d_rotation_matrix(theta)
        d_xy_d_r_i = (d_r_i.T @ scan_xy_i_mat) / Config.SCALE
        d_m_d_r_i = np.sum(d_m_d_xy * d_xy_d_r_i, axis=0)
        d_m_d_t = d_m_d_xy / Config.SCALE
        d_m_d_p = np.vstack([d_m_d_t, d_m_d_r_i[None, :]])

        n_pts_i = scan_odd_i.size
        id_i = np.arange(n_pts, n_pts + n_pts_i)
        n_pts += n_pts_i

        for j in range(n_pts_i):
            for k in range(3):
                jp_id_i.append(id_i[j])
                jp_id_j.append(3 * i + k)
                jp_val.append(d_m_d_p[k, j])

        xy_floor = np.floor(xy)
        u_a, v_a = xy[0], xy[1]
        u_b, v_b = xy_floor[0], xy_floor[1]

        a = (v_b + 1 - v_a) * (u_b + 1 - u_a) / n_inter
        b = (v_a - v_b) * (u_b + 1 - u_a) / n_inter
        c = (v_b + 1 - v_a) * (u_a - u_b) / n_inter
        d = (v_a - v_b) * (u_a - u_b) / n_inter

        d_e_d_m = np.vstack([a, b, c, d])

        a_idx = Config.SIZE_H * v_b + u_b
        b_idx = Config.SIZE_H * (v_b + 1) + u_b
        c_idx = Config.SIZE_H * v_b + u_b + 1
        d_idx = Config.SIZE_H * (v_b + 1) + u_b + 1

        d_e_d_m_id = np.vstack([a_idx, b_idx, c_idx, d_idx])

        for j in range(n_pts_i):
            for k in range(4):
                jd_id_i.append(id_i[j])
                jd_id_j.append(d_e_d_m_id[k, j])
                jd_val.append(d_e_d_m[k, j])

        if i < n_poses - 1:
            cnt_i = 3 * i
            p_a = poses[i]
            p_b = poses[i + 1]
            d_t = r_i.T @ (p_b[:2] - p_a[:2])
            d_phi = wrap_radians(p_b[2] - p_a[2])
            e_o_i = np.zeros(3, np.float64)
            e_o_i[:2] = d_t
            e_o_i[2] = d_phi
            e_o_i = e_o_i - odometry[i + 1]
            e_o_i[2] = wrap_radians(e_o_i[2])
            err_o.append(e_o_i)

            d_t_d_t_a = -r_i.T
            d_t_d_t_b = r_i.T
            d_t_d_phi = d_r_i @ (p_b[:2] - p_a[:2])
            d_phi_d_a = -1.0
            d_phi_d_b = 1.0

            aa = np.arange(3 * i, 3 * i + 3)
            bb = np.arange(3 * (i + 1), 3 * (i + 1) + 3)

            jo_id_i += [
                cnt_i, cnt_i, cnt_i + 1, cnt_i + 1,
                cnt_i, cnt_i, cnt_i + 1, cnt_i + 1,
                cnt_i, cnt_i + 1, cnt_i + 2, cnt_i + 2
            ]
            jo_id_j += [
                aa[0], aa[1], aa[0], aa[1],
                bb[0], bb[1], bb[0], bb[1],
                aa[2], aa[2], aa[2], bb[2]
            ]
            jo_val += [
                d_t_d_t_a[0, 0], d_t_d_t_a[0, 1], d_t_d_t_a[1, 0],
                d_t_d_t_a[1, 1], d_t_d_t_b[0, 0], d_t_d_t_b[0, 1],
                d_t_d_t_b[1, 0], d_t_d_t_b[1, 1], d_t_d_phi[0],
                d_t_d_phi[1], d_phi_d_a, d_phi_d_b
            ]

    err_s = np.concatenate(err_s)
    err_o = np.concatenate(err_o)

    jp = sp.coo_matrix(
        (jp_val, (jp_id_i, jp_id_j)),
        shape=(err_s.size, 3 * n_poses)
    ).tocsc()
    jd = sp.coo_matrix(
        (jd_val, (jd_id_i, jd_id_j)),
        shape=(err_s.size, Config.SIZE_W * Config.SIZE_H)
    ).tocsc()
    jo = sp.coo_matrix(
        (jo_val, (jo_id_i, jo_id_j)),
        shape=(3 * (n_poses - 1), 3 * n_poses)
    ).tocsc()

    i_o, i_s = get_i_matrices(odometry, err_s)

    return jp, jd, jo, i_s, i_o, err_s, err_o