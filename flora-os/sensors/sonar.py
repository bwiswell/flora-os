from ..common import FineMotor

from .mouth import Mouth


class Sonar:

    PORT = 'A'

    def __init__ (self, mouth: Mouth):
        self.motor = FineMotor(Sonar.PORT, plimit = 0.7)
        self.mouth = mouth


    ### METHODS ###
    def scan (self) -> tuple[list[int], list[float], list[float]]:
        angles: list[int] = []
        left: list[float] = []
        right: list[float] = []

        expression, mood = self.mouth.expression, self.mouth.mood

        def callback (idx: int, angle: int):
            angles.append(angle)
            # TODO: measure result of sonar
            self.mouth.sonar(idx)

        self.motor.sweep(-90, 90, 15, callback)
        
        self.mouth.update(expression, mood)

        return angles, left, right