import numpy as np
from typing import Union


class Config:
    MODE_MULTI = True

    WEIGHT_S = 0.3
    WEIGHT_THETA = 600.0
    WEIGHT_XY = 150.0

    DOWN_ITERS = 20
    DOWN_RATE = 10

    MAP_SMOOTHING_WEIGHT_FIRST = 1e-7
    MAP_SMOOTHING_WEIGHT_SECOND = 2.0

    # Smooth n2
    WEIGHT_SMOOTH_N = 1.0

    MAX_ITERS = DOWN_ITERS + 3
    MIN_DELTA = 100
    MIN_DELTA_P = 0.0002
    MIN_MEAN_DELTA_FIRST = 100
    MIN_MEAN_DELTA_POSE_FIRST = 0.0002

    SIZE_I = 100000
    SIZE_J = 100000

    FREE = -0.405465108108164
    OCCUPIED = 0.847297860387203


    # Odometry info
    WEIGHT_O = 0.25

    # Sensor (HC-SR04) info
    MAX_RANGE_METERS = 3.0

    # Calculate bounds
    MIN_ERROR_METERS = 0.75
    MIN_ERROR_PIXELS = 5


    def __init__ (
                self,
                beams: int,
                scale: float    
            ):
        self.beams = beams
        self.scale = scale


    ### PROPERTIES ###

    # Calculate bounds
    @property
    def sel_n_cell (self) -> int:
        return max(
            Config.MIN_ERROR_PIXELS,
            int(np.ceil(Config.MIN_ERROR_METERS / self.scale))
        )
    
    @property
    def var_mask_iters (self) -> int:
        d_theta = (2 * np.pi) / self.beams
        max_gap = Config.MAX_RANGE_METERS * d_theta
        return np.clip(
            int(np.ceil(0.5 * max_gap / self.scale)),
            2, 10
        )
    

    ### METHODS ###

    # Calculate deltas
    def delta_solver_params (self, n: int) -> dict[str, Union[int, float]]:
        tol = self.scale * 0.01
        max_iters = int(np.clip(np.sqrt(n) * 10, 50, 1000))
        return { 'tol': tol, 'atol': tol * 0.1, 'maxiter': max_iters }