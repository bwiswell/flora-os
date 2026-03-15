import numpy as np
from typing import Union


class Config:
    DOWN_ITERS = 20
    MAX_ITERS = DOWN_ITERS + 3
    MIN_DELTA = 100
    MIN_DELTA_P = 0.0002
    MIN_MEAN_DELTA_FIRST = 100
    MIN_MEAN_DELTA_POSE_FIRST = 0.0002

    # Constants
    FREE = -0.405465108108164
    OCCUPIED = 0.847297860387203

    # Odometry info
    CONFIDENCE_ODOM = 0.2
    WEIGHT_ODOM = 0.25

    # Sensor (HC-SR04) info
    CONE_HALF_WIDTH = np.radians(7.5)
    MAX_RANGE_M_SONAR = 3.0

    # Calculate bounds
    MIN_ERROR_METERS = 0.75
    MIN_ERROR_PIXELS = 5

    # Select Laplacian
    SELECT_BASE_SMOOTHING = 8.0


    def __init__ (
                self,
                down_rate: int,
                grid_size: tuple[int, int],
                scale: float
            ):
        self.down_rate = down_rate
        req_j, req_i = grid_size
        self.size_i = (req_i // down_rate) * down_rate
        self.size_j = (req_j // down_rate) * down_rate
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
        max_gap = Config.MAX_RANGE_M_SONAR * Config.CONE_HALF_WIDTH
        return np.clip(
            int(np.ceil(max_gap / self.scale)),
            2, 12
        )

    # Odometry identity matrix
    @property
    def weight_theta (self) -> float:
        return Config.CONFIDENCE_ODOM * 50.0
    
    @property
    def weight_xy (self) -> float:
        return Config.CONFIDENCE_ODOM * (1.0 / self.scale**2)
    
    # Select Laplacian
    @property
    def select_smoothing_weight (self) -> float:
        return Config.SELECT_BASE_SMOOTHING / self.scale


    ### METHODS ###

    # Calculate deltas
    def delta_solver_params (
                self,
                n_vars: int
            ) -> dict[str, Union[int, float]]:
        tol = self.scale * 0.01
        max_iters = int(np.clip(np.sqrt(n_vars) * 10, 50, 1000))
        return { 'tol': tol, 'atol': tol * 0.1, 'maxiter': max_iters }

    # Down/upsampling
    def downsample (self):
        self.size_i = self.size_i // self.down_rate
        self.size_j = self.size_j // self.down_rate
        self.scale = self.scale * self.down_rate

    def upsample (self):
        self.size_i *= self.down_rate
        self.size_j *= self.down_rate
        self.scale /= self.down_rate

    # Smooth n2
    def smooth_solver_params (
                self,
                select: bool,
                n_vars: int
            ) -> dict[str, Union[int, float]]:
        diff = 0.1 / self.scale
        base_iters = int(np.sqrt(n_vars) * diff)
        max_iters = int(np.clip(base_iters, 100, 1000))
        tol = 1e-3 if select else 5e-5
        return { 'tol': tol, 'atol': tol * 0.1, 'maxiter': max_iters}