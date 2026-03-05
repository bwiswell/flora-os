from __future__ import annotations

import asyncio
from typing import Optional

from .io import IO
from .message import Message, MessageType
from .relay import Relay


class Client(IO):
    
    HOSTNAME = 'flora.local'
    PORT = '25565'

    def __init__ (self, name: str, relay: Relay):
        self.name = name
        self.relay = relay

    
    ### CLASS METHODS ###
    @classmethod
    async def connect (cls, name: str) -> Client:
        while True:
            try:
                reader, writer = await asyncio.open_connection(
                    Client.HOSTNAME,
                    IO.PORT
                )
                relay = Relay(reader, writer)
                relay.start()
                await relay.put(Message(MessageType.INIT, name))
                print(f'{name} module connected')
                return Client(name, Relay(reader, writer))
            except:
                print('failed to connect, retrying...')
                await asyncio.sleep(1)
    

    ### METHODS ###
    async def close (self):
        await self.relay.close()

    async def get (self) -> Optional[Message]:
        return await self.relay.get()

    async def put (self, msg: Message):
        await self.relay.put(msg)