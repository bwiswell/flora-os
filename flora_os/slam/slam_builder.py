import numpy as np

from ..common import Pose, Scan

from .slam_data import SLAMData


class SLAMBuilder:

    def __init__ (self):
        self.poses: list[np.ndarray] = []
        self.scans: list[np.ndarray] = []


    ### PROPERTIES ###
    @property
    def slam_data (self) -> SLAMData:
        poses = np.array(self.poses)
        scans = np.array(self.scans)
        return SLAMData(poses, scans)


    ### METHODS ###
    def add_measurement (self, pose: Pose, scan: Scan):
        self.poses.append(pose.ndarray)
        self.scans.append(scan.ndarray)