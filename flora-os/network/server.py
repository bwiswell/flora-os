from __future__ import annotations

import asyncio
from threading import Thread
from typing import Optional

from .message import Message, MessageType
from .relay import Relay


class Server(Thread):

    PORT = '25565'

    def __init__ (self):
        Thread.__init__(self, target=self._start_server)
        self.sensors: Relay = None
        self.traction: Relay = None
        self.start()


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
        server = await asyncio.start_server(self._serve, port = Server.PORT)
        async with server:
            await server.serve_forever()

    def _start_server (self):
        asyncio.run(self._server())

    ### METHODS ###
    def close (self):
        self.sensors.close()
        self.traction.close()

    def get (self) -> Optional[Message]:
        msg = self.sensors.get()
        if msg is None:
            msg = self.traction.get()
        return msg
    
    def put (self, msg: Message):
        if msg.dest == 'sensors':
            self.sensors.put(msg)
        else:
            self.traction.put(msg)

    async def wait_for_ready (self):
        while self.sensors is None or self.traction is None:
            asyncio.sleep(0.2)
        print('starting FLORA...')