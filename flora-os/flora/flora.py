from __future__ import annotations

import asyncio

from ..common import DistanceSensor
from ..controller import Controller
from ..network import Message, MessageType, Server


class Flora(Controller):

    COLLISION_ECHO = 1
    COLLISION_INTERVAL = 1.0
    COLLISION_THRESHOLD = 0.4
    COLLISION_TRIGGER = 2

    def __init__ (self, server: Server):
        Controller.__init__(self, server)

        # Collision tasking/event flags
        self.collision: asyncio.Task = None
        self.collision_sensor = DistanceSensor(
            Flora.COLLISION_ECHO,
            Flora.COLLISION_TRIGGER
        )
        self.collision_warning = asyncio.Event()

        # Sonar tasking/event flags
        self.sonar: asyncio.Task = None
        self.last_sonar: tuple[list[int], list[float], list[float]] = None
        self.sonar_update = asyncio.Event()


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Flora:
        server = await Server.connect('flora')
        return Flora(server)
    

    ### HELPERS ###
    async def _collision (self):
        while True:
            if self.collision_warning.is_set():
                if self.collision_sensor.distance > Flora.COLLISION_THRESHOLD:
                    self.collision_warning.clear()
            else:
                if self.collision_sensor.distance <= Flora.COLLISION_THRESHOLD:
                    self.collision_warning.set()
            await asyncio.sleep(Flora.COLLISION_INTERVAL)

    async def _sonar (self):
        await self.send(Message.scan())
        await self.sonar_update.wait()
        # TODO: handle new sonar data
        self.sonar_update.clear()


    ### METHODS ###
    async def exit (self):
        self.collision.cancel()
        await self.io.close()

    async def handle_message (self, msg: Message):
        print(f'handling {msg.type}...')
        if msg.type == MessageType.SONAR:
            self.last_sonar = Message.decode_sonar(msg)
            self.sonar_update.set()

    async def setup (self):
        self.collision = asyncio.create_task(self._collision())

    async def update (self):
        pass