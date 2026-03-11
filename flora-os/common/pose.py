from __future__ import annotations

import math

import numpy as np
import seared as s


@s.seared
class Pose(s.Seared):

    x: float = s.Float(required=True)
    y: float = s.Float(required=True)
    theta: float = s.Float(required=True)

    def __init__ (self, x: float = 0.0, y: float = 0.0, theta: float = 0.0):
        self.x = x
        self.y = y
        self.theta = theta


    ### PROPERTIES ###
    def inverse (self) -> Pose:
        cos = math.cos(self.theta)
        sin = math.sin(self.theta)
        x = -cos * self.x - sin * self.y
        y = sin * self.x - cos * self.y
        return Pose(x, y, -self.theta)

    def matrix (self) -> np.ndarray:
        cos = math.cos(self.theta)
        sin = math.sin(self.theta)
        return np.array([
            [cos, -sin, self.x],
            [sin, cos, self.y],
            [0.0, 0.0, 1.0]
        ])