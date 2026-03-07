from __future__ import annotations

import asyncio
from typing import Optional

from .io import IO
from .message import Message
from .relay import Relay


class Server(IO):

    def __init__ (self):
        IO.__init__(self, 'flora')
        self.sensors: Relay = None
        self.traction: Relay = None
        self.incoming: asyncio.Queue = asyncio.Queue()
        self.outgoing: asyncio.Queue = asyncio.Queue()


    ### HELPERS ###
    async def _serve (
                self,
                reader: asyncio.StreamReader,
                writer: asyncio.StreamWriter
            ):
        relay = Relay(reader, writer)
        init = await relay.wait_for_get()
        if init.src == 'sensors':
            print('sensor module connected')
            self.sensors = relay
        else:
            print('traction module connected')
            self.traction = relay

    ### METHODS ###
    async def close (self):
        print('broadcasting exit message...')
        await self.write(Message.exit('sensors'))
        await self.write(Message.exit('traction'))
        print('waiting for modules to exit...')
        await asyncio.sleep(3)
        print('closing sockets...')
        await self.sensors.close()
        await self.traction.close()
        print('server closed')

    async def read (self) -> Optional[Message]:
        msg = await self.sensors.read()
        if msg is None:
            msg = await self.traction.read()
        return msg

    async def serve (self):
        server = await asyncio.start_server(self._serve, port = IO.PORT)
        async with server:
            await server.serve_forever()
    
    async def write (self, msg: Message):
        if msg.dest == 'sensors':
            await self.sensors.write(msg)
        else:
            await self.traction.write(msg)

    async def wait_for_ready (self):
        while self.sensors is None or self.traction is None:
            print('waiting for modules to connect...')
            asyncio.sleep(5)
        print('starting FLORA...')