from __future__ import annotations

import asyncio

from .network import IO, Message, MessageType


class Controller:

    INTERRUPT = 0.3

    def __init__ (self, io: IO):
        self.io = io
        self.running = True


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Controller:
        raise NotImplementedError


    ### HELPERS ###
    async def _handle_message (self):
        msg = await self.io.read()
        if msg is not None:
            print(f'found {msg.type} to handle')
            self.handle_message(msg)


    ### METHODS ###
    async def exit (self):
        await self.io.close()

    def handle_message (self, msg: Message):
        raise NotImplementedError
    
    async def run (self):
        await self.setup()
        while self.running:
            await self._handle_message()
            await self.update()
            await asyncio.sleep(Controller.INTERRUPT)
        print(f'closing {self.io.name} module...')
        await self.exit()

    async def send (self, msg: Message):
        await self.io.write(msg)

    async def setup (self):
        raise NotImplementedError

    async def update (self):
        raise NotImplementedError