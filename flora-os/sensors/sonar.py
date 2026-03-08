import asyncio

from ..common import DistanceSensor, FineMotor

from .mouth import Mouth


class Sonar:

    LEFT_ECHO = 1
    LEFT_TRIGGER = 2
    PORT = 'A'
    RIGHT_ECHO = 3
    RIGHT_TRIGGER = 4

    def __init__ (self, mouth: Mouth):
        self.motor = FineMotor(Sonar.PORT, plimit = 0.7)
        self.mouth = mouth
        self.left = DistanceSensor(Sonar.LEFT_ECHO, Sonar.LEFT_TRIGGER)
        self.right = DistanceSensor(Sonar.RIGHT_ECHO, Sonar.RIGHT_TRIGGER)


    ### HELPERS ###
    async def _measure (self) -> tuple[float, float]:
        left, right = await asyncio.gather(
            asyncio.create_task(self.left.measure()),
            asyncio.create_task(self.right.measure())
        )
        return left, right


    ### METHODS ###
    async def scan (self) -> tuple[list[int], list[float], list[float]]:
        angles: list[int] = []
        left: list[float] = []
        right: list[float] = []

        expression, mood = self.mouth.expression, self.mouth.mood

        async def callback (idx: int, angle: int):
            angles.append(angle)
            l, r = await self._measure()
            left.append(l)
            right.append(r)
            self.mouth.sonar(idx)

        await self.motor.sweep(-90, 90, 15, callback)
        
        self.mouth.update(expression, mood)

        return angles, left, right