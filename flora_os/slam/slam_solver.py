import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..util import rotation_matrix, wrap_radians

from .config import Config
from .util import smooth_n2


class SLAMSolver:

    @classmethod
    def bilinear_interpolation (
                cls,
                grid: np.ndarray,
                xy: np.ndarray
            ) -> np.ndarray:
        n_pts = xy.shape[0]
        inter = np.ndarray((n_pts), np.float64)
        for i in range(n_pts):
            x = xy[i, 0]
            y = xy[i, 1]
            i_a = math.floor(y)
            i_b = i_a + 1
            j_a = math.floor(x)
            j_b = j_a + 1
            if i_a < 0 or i_b >= grid.shape[0] or \
                    j_a < 0 or j_b >= grid.shape[1]:
                inter[i] = 0.0
                continue
            q_a_a = grid[i_a, j_a]
            q_b_a = grid[i_a, j_b]
            q_a_b = grid[i_b, j_a]
            q_b_b = grid[i_b, j_b]
            w_a = (j_b - x) * q_a_a + (x - j_a) * q_b_a
            w_b = (j_b - x) * q_a_b + (x - j_a) * q_b_b
            w = (i_b - y) * w_a + (y - i_a) * w_b
            inter[i] = w
        return inter


    @classmethod
    def delta (
                cls,
                grid: np.ndarray,
                jp: sp.csc_matrix,
                jd: sp.csc_matrix,
                jo: sp.csc_matrix,
                err_s: np.ndarray,
                err_o: np.ndarray,
                i_o: sp.csc_matrix,
                weighted_hh: sp.csc_matrix
            ) -> tuple[
                np.ndarray,
                np.ndarray,
                float,
                float
            ]:
        jp_s = jp[:, 3:].tocsc()
        jo_s = jo[:, 3:].tocsc()

        u = jp_s.T @ jp_s + Config.WEIGHT_O * (jo_s.T @ i_o @ jo_s)
        v = jd.T @ jd + weighted_hh
        w = jp_s.T @ jd

        e_p = -jp_s.T @ err_s - Config.WEIGHT_O * (jo_s.T @ i_o @ err_o)
        e_d = -jd.T @ err_s
        xh = grid.T.flatten()
        e_h = -weighted_hh @ xh
        e_d_e_h = e_d + e_h

        i_i = sp.bmat([[u, w], [w.T, v]], 'csc')
        e_e = np.concatenate((e_p, e_d_e_h))

        max_iter = min(200, int(np.floor(np.sqrt(i_i.shape[0]))))

        delta, _ = spl.cg(i_i, e_e, tol=0.005, maxiter=max_iter)

        num_p = jp_s.shape[1]
        delta_p = delta[:num_p]
        delta_d = delta[num_p:]

        total_delta = np.dot(delta, delta)
        mean_delta = total_delta / delta.size

        total_delta_p = np.dot(delta_p, delta_p)
        mean_delta_p = total_delta_p / delta_p.size

        return delta_p, delta_d, mean_delta, mean_delta_p


    @classmethod
    def diff_jacobian (
                cls,
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
        g_v, g_u = SLAMSolver.gradient(grid, h)
        n_pts = 0

        jp_id_i, jp_id_j, jp_val = [], [], []
        jd_id_i, jd_id_j, jd_val = [], [], []
        jo_id_i, jo_id_j, jo_val = [], [], []
        err_s, err_o = [], []

        for i in range(n_poses):
            theta = poses[i, 2]
            r_i = rotation_matrix(theta)

            scan_xy_i = scan_xy[i].reshape(2, -1, 'F')
            scan_odd_i = scan_odd[i]

            xy = ((r_i @ scan_xy_i) + poses[i, :2]) / Config.SCALE
            
            grid_inter = SLAMSolver.bilinear_interpolation(grid, xy.T)
            n_inter = SLAMSolver.bilinear_interpolation(n, xy.T)

            err_s.append(grid_inter / n_inter - scan_odd_i)

            g_u_inter = SLAMSolver.bilinear_interpolation(g_u, xy.T)
            g_v_inter = SLAMSolver.bilinear_interpolation(g_v, xy.T)

            d_m_d_xy = np.vstack([g_u_inter / n_inter, g_v_inter / n_inter])
            d_r_i = SLAMSolver.d_rotation_matrix(theta)
            d_xy_d_r_i = (d_r_i.T @ scan_xy_i) / Config.SCALE
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

        i_s, i_o = SLAMSolver.get_i_matrices(odometry, err_s)

        return jp, jd, jo, i_s, i_o, err_s, err_o


    @classmethod
    def d_rotation_matrix (cls, theta: float) -> np.ndarray:
        c, s = math.cos(theta), math.sin(theta)
        return np.array([[-s, c], [-c, -s]])
    

    @classmethod
    def get_i_matrices (
                cls,
                odometry: np.ndarray,
                err_s: np.ndarray
            ) -> tuple[sp.csc_matrix, sp.csc_matrix]:
        i_s = sp.identity(err_s.size, np.float64, 'csc')
        i_s.setdiag(1.0)
        n_o = odometry.shape[0] - 1
        sig_o = np.array([400.0, 400.0, 2500.0])
        diag_sig_o = np.tile(sig_o, (n_o, 1)).reshape(-1)
        i_o = sp.identity(3 * n_o, np.float64, 'csc')
        i_o.setdiag(diag_sig_o)
        return i_s, i_o


    @classmethod
    def gradient (
                cls,
                grid: np.ndarray,
                h: float
            ) -> tuple[np.ndarray, np.ndarray]:
        g_x = np.ndarray(grid.shape, np.float64)
        g_y = np.ndarray(grid.shape, np.float64)

        g_x[0, :] = (grid[1, :] - grid[0, :]) / h
        g_x[-1, :] = (grid[-1, :] - grid[-2, :]) / h
        g_x[1:-1, :] = (grid[2:, :] - grid[0:-2, :]) / (2 * h)

        g_y[:, 0] = (grid[:, 1] - grid[:, 0]) / h
        g_y[:, -1] = (grid[:, -1] - grid[:, -2]) / h
        g_y[:, 1:-1] = (grid[:, 2:] - grid[:, 0:-2]) / (2 * h)

        return g_x, g_y

    
    @classmethod
    def solve (
                cls,
                grid: np.ndarray,
                n: np.ndarray,
                poses: np.ndarray,
                odometry: np.ndarray,
                scan_xy: list[np.ndarray],
                scan_odd: list[np.ndarray],
                low_scan_xy: list[np.ndarray],
                low_scan_odd: list[np.ndarray],
                hh: sp.csc_matrix
            ):
        s_w = Config.SIZE_W * Config.DOWN_RATE
        s_h = Config.SIZE_H * Config.DOWN_RATE

        weighted_hh = hh * Config.MAP_SMOOTHING_WEIGHT_FIRST

        sel_grid = np.ndarray((s_w, s_h), np.float64)
        sel_n = np.ndarray((s_w, s_h), np.float64)
        sel_scan_xy: list[np.ndarray] = []
        sel_scan_odd: list[np.ndarray] = []
        sel_weighted_hh: sp.csc_matrix = None

        iters = 0
        mean_delta = 100000
        mean_delta_p = 100

        while mean_delta_p > Config.MIN_DELTA_P and \
                mean_delta > Config.MIN_DELTA and iters < Config.MAX_ITERS:
            if iters < Config.DOWN_ITERS:
                jp, jd, jo, i_s, i_o, err_s, err_o = SLAMSolver.diff_jacobian(
                    grid,
                    n,
                    poses,
                    odometry,
                    low_scan_xy,
                    low_scan_odd
                )

                delta_p, delta_d, mean_delta, mean_delta_p = SLAMSolver.delta(
                    grid,
                    jp,
                    jd,
                    jo,
                    err_s,
                    err_o,
                    i_o,
                    weighted_hh
                )

                SLAMSolver.update(grid, poses, delta_p, delta_d)
                n[:, :] = SLAMSolver.update_grid_n(poses, low_scan_xy)[:, :]
                if mean_delta < Config.MIN_MEAN_DELTA_FIRST:
                    Config.DOWN_ITERS = iters
                    Config.MAX_ITERS = Config.DOWN_ITERS + 3
                n[:, :] = SLAMSolver.smooth_n2(n, hh)[:, :]
            elif Config.MODE_MULTI and iters >= Config.DOWN_ITERS:
                if iters == Config.DOWN_ITERS:
                    Config.SIZE_W *= Config.DOWN_RATE
                    Config.SIZE_H *= Config.DOWN_RATE
                    Config.SCALE /= Config.DOWN_RATE
                    


    @classmethod
    def smooth_n2 (n: np.ndarray, hh: sp.csc_matrix) -> np.ndarray:
        rows, cols = np.nonzero(n)
        vals = n[rows, cols]
        n_nz = rows.shape[0]
        id_i = np.array(list(range(n_nz)), np.int32)
        id_j = rows * Config.SIZE_H + cols
        np_ones = np.ones((n_nz))
        ones = sp.csc_matrix(
            (np_ones, (id_i, id_j)),
            (n_nz, Config.SIZE_W * Config.SIZE_H),
            np.float64
        )
        ii = ones.T @ ones + hh
        ee = ones.T * vals
        solve = spl.factorized(ii)
        delta_n: np.ndarray = solve(ee)
        return delta_n.reshape((Config.SIZE_H, Config.SIZE_W)).T                


    @classmethod
    def update (
                cls,
                grid: np.ndarray,
                poses: np.ndarray,
                delta_p: np.ndarray,
                delta_d: np.ndarray
            ):
        delta_p_mat = delta_p.reshape((-1, 3), order='F')
        poses[1:, :] += delta_p_mat
        size_w, size_h = grid.shape
        delta_d_mat = delta_d.reshape((size_h, size_w), order='F').T
        grid += delta_d_mat


    @classmethod
    def update_grid_n (
                cls,
                poses: np.ndarray,
                scan_xy: list[np.ndarray]
            ) -> np.ndarray:
        n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
        n_poses = poses.shape[0]
        for i in range(n_poses):
            r_i = rotation_matrix(poses[i, 2])
            scan_xy_i = scan_xy[i].reshape((2, -1), order='F')
            pose_vec = poses[i, :].T
            s_i = (r_i @ scan_xy_i) + pose_vec
            xy = (s_i / Config.SCALE).round().astype(np.int32)
            temp_n = np.zeros((Config.SIZE_W, Config.SIZE_H), np.float64)
            for j in range(xy.shape[1]):
                row, col = xy[0, j], xy[1, j]
                temp_n[row, col] += 1
            n += temp_n
        return n