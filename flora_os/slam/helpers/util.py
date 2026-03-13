import math

import numpy as np


def d_rotation_matrix (theta: float) -> np.ndarray:
    '''
    Returns the 2D derivative of the standard rotation matrix for the given
    angle `theta` (in radians).

    Parameters:
        theta (`float`):
            The angle (in radians) to create rotation matrix derivative from.

    Returns:
        d_rotation_matrix (`ndarray`):
            A 2D `ndarray` with shape (2, 2) representing the derivative of the
            standard rotation transform matrix for `theta`

            [[-`s`, `c`],\n
             [`-c`, `-s`]]

            where `c` is the cosine of `theta` and `s` is the sine of `theta`.
    '''
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[-s, c], [-c, -s]])


def rotation_matrix (theta: float) -> np.ndarray:
    '''
    Returns the 2D rotation matrix for the given angle `theta` (in radians).

    Parameters:
        theta (`float`):
            The angle (in radians) to create a rotation matrix from.

    Returns:
        rotation_matrix (`ndarray`):
            A 2D `ndarray` with shape (2, 2) representing the standard rotation
            transform matrix for `theta`

            [[`c`, -`s`],\n
             [`s`, `c`]]

            where `c` is the cosine of `theta` and `s` is the sine of `theta`.
    '''
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s], [s, c]])


def wrap_radians (theta: float) -> float:
    '''
    Returns an equivalent angle (in radians) to `val` in the range
    (-`pi`, `pi`).

    Parameters:
        theta (`float`):
            The angle (in radians) to convert.

    Returns:
        theta_prime (`float`):
            An equivalent angle (in radians) in the range (-`pi`, `pi`).
    '''
    r = theta
    while r < -math.pi:
        r += 2 * math.pi
    while r > math.pi:
        r -= 2 * math.pi
    return r