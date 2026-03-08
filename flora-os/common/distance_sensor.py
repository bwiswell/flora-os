from __future__ import annotations

import asyncio

from gpiozero import DistanceSensor as GZDistanceSensor


class DistanceSensor:

    MEASURE_INTERVAL = 0.6

    def __init__ (self, echo: int, trigger: int):
        self.sensor = GZDistanceSensor(
            echo = echo,
            trigger = trigger,
            max_distance = 3,
            threshold_distance = 0.1
        )


    ### PROPERTIES ###
    @property
    def distance (self) -> float:
        return self.sensor.distance


    ### METHODS ###
    def close (self):
        self.sensor.close()

    async def measure (self) -> float:
        await asyncio.sleep(DistanceSensor.MEASURE_INTERVAL)
        return self.distance