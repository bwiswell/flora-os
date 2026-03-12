from __future__ import annotations

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
    @property
    def ndarray (self) -> np.ndarray:
        return np.array([self.x, self.y, self.theta])