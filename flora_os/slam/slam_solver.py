import math
import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from .config import Config
from .helpers import (
    initialize_odometry
)


class SLAMSolver:

    def __init__ (
                self,
                config: Config,
                imu_poses: npt.NDArray[np.float64],
                scans: npt.NDArray[np.float64]
            ):
        self.config = config
        self.imu_poses = imu_poses
        self.odometry, self.poses = initialize_odometry(imu_poses)
        self.scans = scans


    