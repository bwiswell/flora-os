from __future__ import annotations

import asyncio

from .network import IO, Message


class Controller:

    def __init__ (self, io: IO):
        self.io = io
        asyncio.run(self.run())


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
        raise NotImplementedError
    
    async def run (self):
        await self._handle_message()
        await self.update()

    async def send (self, msg: Message):
        await self.io.put(msg)

    async def update (self):
        raise NotImplementedError