from __future__ import annotations

import asyncio

from .network import IO, Message, MessageType


class Controller:

    def __init__ (self, io: IO):
        self.io = io
        self.running = True


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Controller:
        raise NotImplementedError


    ### HELPERS ###
    async def _handle_message (self):
        msg = await self.io.get()
        if msg is not None:
            self.handle_message(msg)


    ### METHODS ###
    def handle_message (self, msg: Message):
        if msg.type == MessageType.EXIT:
            self.running = False
    
    async def run (self):
        while self.running:
            await self._handle_message()
            await self.update()
        print(f'closing {self.io.name} module...')
        await self.io.close()

    async def send (self, msg: Message):
        await self.io.put(msg)

    async def update (self):
        raise NotImplementedError