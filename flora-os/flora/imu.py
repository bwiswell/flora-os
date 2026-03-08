import asyncio
import math
import time
from typing import Optional

from filterpy.kalman import KalmanFilter
import numpy as np
from sense_hat import SenseHat

from ..common import Pos


class IMU:

    GRAVITY = 9.80665
    MEASURE_NOISE = 5.0
    PROCESS_NOISE = 0.1
    STILL_ACC_THRESHOLD = 0.15
    STILL_DURATION = 0.5
    STILL_ROT_THRESHOLD = math.radians(2.0)
    UNCERTAINTY = 1000.0
    UPDATE_FREQ = 0.05
    
    def __init__ (self, hat: SenseHat):
        self.hat = hat

        self.task: asyncio.Task = None

        self.write_lock = asyncio.Lock()
        self.pos = Pos()
        self._heading = 0.0

        self.kfx = self._get_kf()
        self.kfy = self._get_kf()

        self.last = time.time()
        self.still_start: Optional[float] = None


    ### PROPERTIES ###
    @property
    def acc_xy (self) -> tuple[float, float]:
        acc = self.hat.get_accelerometer_raw()
        return acc['x'] * IMU.GRAVITY, acc['y'] * IMU.GRAVITY

    @property
    def acc_yaw (self) -> float:
        return self.hat.get_gyroscope_raw()['z']

    @property
    def heading (self) -> float:
        return math.degrees(self._heading)
    

    ### HELPERS ###
    def _get_kf (self):
        kf = KalmanFilter(dim_x = 3, dim_z = 1)
        kf.x = np.array([0.0, 0.0, 0.0])
        kf.F = np.array([
            [1.0, IMU.UPDATE_FREQ, 0.5 * IMU.UPDATE_FREQ**2],
            [0.0, 1.0, IMU.UPDATE_FREQ],
            [0.0, 0.0, 1.0]
        ])
        kf.H = np.array([[0.0, 0.0, 1.0]])
        kf.P *= IMU.UNCERTAINTY
        kf.R = IMU.MEASURE_NOISE
        kf.Q = IMU.PROCESS_NOISE
        return kf

    async def _run (self):
        while True:
            await self.write_lock.acquire()

            curr = time.time()
            a_yaw = self.acc_yaw
            a_x, a_y = self.acc_xy

            d_t = curr - self.last

            d_yaw = a_yaw * d_t
            head = self._heading + d_yaw

            a_gx = a_x * math.cos(head) - a_y * math.sin(head)
            a_gy = a_y * math.sin(head) + a_y * math.cos(head)

            acc_still = math.sqrt(a_gx**2 + a_gy**2) < IMU.STILL_ACC_THRESHOLD
            gyro_still = abs(a_yaw) < IMU.STILL_ROT_THRESHOLD
            
            if acc_still and gyro_still:
                if self.still_start is None:
                    self.still_start = time.time()
                elif (time.time() - self.still_start) > IMU.STILL_DURATION:
                    self.kfx.x[1] = 0.0
                    self.kfy.x[1] = 0.0
                    self.kfx.P[1, 1] *= 0.1
                    self.kfy.P[1, 1] *= 0.1
            else:
                self.still_start = None

            for kf, val in [(self.kfx, a_gx), (self.kfy, a_gy)]:
                kf.F[0, 1] = kf.F[1, 2] = d_t
                kf.F[0, 2] = 0.5 * d_t**2
                kf.predict()
                kf.update(val)

            self.pos = Pos(self.kfx.x[0], self.kfy.x[0])
            self._heading = head
            self.last = curr

            self.write_lock.release()
            await asyncio.sleep(IMU.UPDATE_FREQ - (time.time() - curr))


    ### METHODS ###
    def start (self):
        self.task = asyncio.create_task(self._run())
    
    def stop (self):
        self.task.cancel()

    async def update (
                self,
                pos: Pos,
                heading: Optional[float] = None
            ):
        await self.write_lock.acquire()
        self.pos = pos
        if heading is not None: self.heading = math.radians(heading)
        self.write_lock.release()