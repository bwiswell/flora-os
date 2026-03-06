from typing import TypeVar


Number = TypeVar('Number', int, float)


def clip (val: Number, low: Number, high: Number) -> Number:
    return max(low, min(high, val))

def clip_and_scale (val: float, scale: int, low: int, high: int) -> int:
    return clip(scale(val, scale), low, high)

def scale (val: float, scale: int) -> int:
    return round(val * scale)