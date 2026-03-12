import numpy as np
import seared as s


@s.seared
class SLAMData(s.Seared):

    odometry: np.ndarray = s.NDArray(required=True)
    scans: np.ndarray = s.NDArray(required=True)

    def __init__ (self, odometry: np.ndarray, scans: np.ndarray):
        self.odometry = odometry
        self.scans = scans