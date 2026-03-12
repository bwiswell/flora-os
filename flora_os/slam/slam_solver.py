import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..util import rotation_matrix, wrap_radians

from .config import Config
from .helpers import smooth_n2


class SLAMSolver:    
    
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
        sel_id: np.ndarray = None
        sel_id_var: np.ndarray = None
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
                    high_grid, high_n = SLAMSolver.initialize_grid_map(
                        poses,
                        scan_xy,
                        scan_odd
                    )
                    sel_id, sel_id_var = SLAMSolver.calculate_bounds(high_grid)