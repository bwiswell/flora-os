from ..common import FineMotor


class Sonar:

    PORT = 'A'

    def __init__ (self):
        self.motor = FineMotor(Sonar.PORT, plimit = 0.7)


    ### METHODS ###
    def scan (self) -> tuple[list[int], list[float], list[float]]:
        angles: list[int] = []
        left: list[float] = []
        right: list[float] = []

        def callback (angle: int):
            angles.append(angle)
            # TODO: measure result of sonar

        self.motor.sweep(-90, 90, 15, callback)

        return angles, left, right