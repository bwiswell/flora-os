from __future__ import annotations

import asyncio

from ..controller import Controller
from ..network import Message, MessageType, Server


class Flora(Controller):

    PASSIVE_SONAR_INTERVAL = 10.0

    def __init__ (self, server: Server):
        Controller.__init__(self, server)

        self.sonar: asyncio.Task = None
        self.last_sonar: tuple[list[int], list[float], list[float]] = None
        self.sonar_update = asyncio.Event()


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Flora:
        server = await Server.connect('flora')
        return Flora(server)
    

    ### HELPERS ###
    async def _sonar (self):
        while True:
            await self.send(Message.scan())
            await self.sonar_update.wait()
            # TODO: handle new sonar data
            self.sonar_update.clear()
            await asyncio.sleep(Flora.PASSIVE_SONAR_INTERVAL)


    ### METHODS ###
    async def exit (self):
        self.sonar.cancel()
        await self.io.close()

    async def handle_message (self, msg: Message):
        print(f'handling {msg.type}...')
        if msg.type == MessageType.SONAR:
            self.last_sonar = Message.decode_sonar(msg)
            self.sonar_update.set()

    async def setup (self):
        self.sonar = asyncio.create_task(self._sonar())

    async def update (self):
        pass