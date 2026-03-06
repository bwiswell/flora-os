from __future__ import annotations

import asyncio
from threading import Thread
from typing import Optional

from .io import IO
from .message import Message, MessageType
from .relay import Relay


class Server(IO, Thread):

    def __init__ (self, name):
        Thread.__init__(self, target=self._start_server)
        IO.__init__(self, name)
        self.sensors: Relay = None
        self.traction: Relay = None
        self.start()


    ### CLASS METHODS ###
    @classmethod
    async def connect (cls, name: str = 'flora') -> Server:
        server = Server(name)
        await server.wait_for_ready()
        return server


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
        relay.start()

    async def _server (self):
        server = await asyncio.start_server(self._serve, port = IO.PORT)
        async with server:
            await server.serve_forever()

    def _start_server (self):
        asyncio.run(self._server())

    ### METHODS ###
    async def close (self):
        print('broadcasting exit message...')
        self.put(Message.exit('sensors'))
        self.put(Message.exit('traction'))
        print('waiting for modules to exit...')
        await asyncio.sleep(3)
        print('closing sockets...')
        await self.sensors.close()
        await self.traction.close()
        print('server closed')

    async def get (self) -> Optional[Message]:
        msg = self.sensors.get()
        if msg is None:
            msg = self.traction.get()
        return msg
    
    async def put (self, msg: Message):
        if msg.dest == 'sensors':
            self.sensors.put(msg)
        else:
            self.traction.put(msg)

    async def wait_for_ready (self):
        while self.sensors is None or self.traction is None:
            print('waiting for modules to connect...')
            asyncio.sleep(0.2)
        print('starting FLORA...')