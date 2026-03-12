import numpy as np
import scipy.sparse as sp

from .config import Config


class SLAMSolver:

    @classmethod
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
                np.ndarray,
                float,
                float
            ]:
        n_poses = poses.shape[0]
        h = 1.0
        g_v, g_u = SLAMSolver.gradient(grid, h)
        n_pts = 0


    @classmethod
    def gradient (grid: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray]:
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
        sel_grid = np.ndarray((s_w, s_h), np.float64)
        sel_n = np.ndarray((s_w, s_h), np.float64)
        sel_scan_xy: list[np.ndarray] = []
        sel_scan_odd: list[np.ndarray] = []

        iters = 0
        mean_delta = 100000
        mean_delta_p = 100

        while mean_delta_p > Config.MIN_DELTA_P and \
                mean_delta > Config.MIN_DELTA and iters < Config.MAX_ITERS:
            if iters < Config.DOWN_ITERS:
                