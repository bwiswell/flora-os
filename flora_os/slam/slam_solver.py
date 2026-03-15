import numpy as np
import numpy.typing as npt

from .config import Config
from .helpers import (
    initialize_odometry,
    initialize_scans
)


class SLAMSolver:

    def __init__ (
                self,
                config: Config,
                imu_poses: npt.NDArray[np.float64],
                sonar: npt.NDArray[np.float64]
            ):
        self.config = config
        self.imu_poses = imu_poses
        self.odometry, self.poses = initialize_odometry(imu_poses)
        self.scans, self.pose_idxs = initialize_scans(sonar)