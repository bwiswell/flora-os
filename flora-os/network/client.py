from __future__ import annotations

import asyncio
from typing import Optional

from .io import IO
from .message import Message
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
        tries = 1
        while True:
            try:
                reader, writer = await asyncio.open_connection(
                    Client.HOSTNAME,
                    IO.PORT
                )
                relay = Relay(reader, writer)
                await relay.write(Message.init(name))
                print(f'{name} module connected')
                return Client(name, Relay(reader, writer))
            except:
                print(f'failed to connect, retrying ({tries} attemps)...')
                tries += 1
                await asyncio.sleep(5)
    

    ### METHODS ###
    async def close (self):
        await self.relay.close()

    async def read (self) -> Optional[Message]:
        return await self.relay.read()

    async def write (self, msg: Message):
        await self.relay.write(msg)