import numpy as np

from ..common import Pose, Scan

from .slam_data import SLAMData


class SLAMBuilder:

    def __init__ (self):
        self.odometry: list[np.ndarray] = []
        self.scans: list[np.ndarray] = []


    ### PROPERTIES ###
    @property
    def slam_data (self) -> SLAMData:
        odometry = np.array(self.odometry)
        scans = np.array(self.scans)
        return SLAMData(odometry, scans)


    ### METHODS ###
    def add_measurement (self, pose: Pose, scan: Scan):
        self.odometry.append(pose.ndarray)
        self.scans.append(scan.ndarray)