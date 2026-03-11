import math

import numpy as np
import seared as s


@s.seared
class Scan(s.Seared):

    angles: list[float] = s.Float(many=True, required=True)
    left: list[int] = s.Int(many=True, required=True)
    right: list[int] = s.Int(many=True, required=True)

    def __init__ (
                self,
                angles: list[float],
                left: list[int],
                right: list[int]
            ):
        self.angles = angles
        self.left = left
        self.right = right

    
    ### PROPERTIES ###
    @property
    def ndarray (self) -> np.ndarray:
        angles = [math.radians(ang + 90.0) for ang in self.angles]
        angles.extend([math.radians(ang - 90.0) for ang in self.angles])
        data = self.left + self.right
        return np.array([angles, data]).T
        