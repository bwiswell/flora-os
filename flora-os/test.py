from .common import FineMotor


def test ():
        m = FineMotor('A', 3.0)
        m.sweep(-90, 90, 15, print)