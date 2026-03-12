import math
from typing import TypeVar


Number = TypeVar('Number', int, float)


def clip (val: Number, low: Number, high: Number) -> Number:
    return max(low, min(high, val))

def clip_and_scale (val: float, scalar: int, low: int, high: int) -> int:
    return clip(scale(val, scalar), low, high)

def clip_radians (val: float) -> float:
    r = val
    while r < -math.pi:
        r += 2 * math.pi
    while r > math.pi:
        r -= 2 * math.pi
    return r

def scale (val: float, scale: int) -> int:
    return round(val * scale)