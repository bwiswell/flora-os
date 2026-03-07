from typing import Awaitable, Callable, Literal

from buildhat import Motor


Direction = Literal['clockwise', 'anticlockwise', 'shortest']


class FineMotor:
    
    def __init__ (
                self,
                port: str,
                ratio: float = 1.0,
                bias: int = 0,
                plimit: float = 1.0
            ):
        self.motor = Motor(port)
        self.motor.plimit(plimit)
        self.ratio = ratio
        self.bias = bias
        self.reset()


    ### HELPERS ###
    def _from_motor_apos (
                self,
                apos: int,
                was_positive: bool,
                was_zero: bool
            ) -> int:
        if was_zero:
            normalized = apos
        elif apos < 0 and was_positive:
            normalized = 180 + (apos + 180)
        elif apos > 0 and not was_positive:
            normalized = -180 - (180 - apos)
        else:
            normalized = apos
        return round(normalized / self.ratio) + self.bias

    def _to_motor_apos (self, apos: int) -> int:
        scaled = round((apos - self.bias) * self.ratio)
        if scaled < -180:
            return 180 - (-180 - scaled)
        elif scaled > 180:
            return -180 + (scaled - 180)
        else:
            return scaled
        

    ### METHODS ###
    def reset (self, dir: Direction = 'shortest'):
        self.run_to_position(0, dir)

    def run_to_position (
                self,
                degrees: int,
                dir: Direction = 'shortest',
                blocking: bool = True,
                speed_limit: int = 100
            ) -> int:
        was_positive = degrees >= 0
        was_zero = degrees == 0
        apos = self._to_motor_apos(degrees)
        for speed in [100, 75, 50, 40]:
            if speed_limit >= speed:
                self.motor.run_to_position(apos, speed, blocking, dir)
        self.motor.run_to_position(apos, max(30, speed_limit), blocking, dir)
        result = self._from_motor_apos(
            self.motor.get_aposition(),
            was_positive,
            was_zero
        )
        print(f'target: {degrees}, result: {result}')
        return result

    def sweep (
                self,
                start: int,
                end: int,
                interval: int,
                callback: Callable[[int, int], None]
            ):
        curr = self.motor.get_aposition()
        if abs(curr) > 5:
            self.reset('shortest')
        res = self.run_to_position(start, 'anticlockwise')
        callback(0, res)
        for i, angle in enumerate(range(start + interval, end + 1, interval)):
            res = self.run_to_position(angle, 'clockwise')
            callback(i, res)
        self.reset('anticlockwise')