import time

from .common import Expression, FineMotor, Mood
from .sensors import Mouth


last = Expression.OPEN
m = Mouth()

def callback (angle: int):
    global last
    last = Expression.CORNERS if last == Expression.OPEN else Expression.OPEN
    time.sleep(1)
    m.update(last, Mood.CURIOUS)


def test ():
    m.update(Expression.FLAT, Mood.NONE)
    time.sleep(3)
    m.update(Expression.SMILE, Mood.HAPPY)
    time.sleep(3)
    m.update(Expression.OPEN, Mood.CURIOUS)
    s = FineMotor('B', 3.0, bias=-1)
    s.sweep(-90, 90, 15, callback)
    m.update(Expression.RESTING, Mood.NONE)
    time.sleep(3)

