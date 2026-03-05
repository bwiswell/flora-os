from __future__ import annotations

import asyncio
from typing import Optional

from .message import Message
from .relay import Relay


class Client:
    
    HOSTNAME = 'flora.local'
    PORT = '25565'

    def __init__ (self, name: str, relay: Relay):
        self.name = name
        self.relay = relay
        self.relay.start()

    
    ### CLASS METHODS ###
    @classmethod
    async def connect (cls, name: str) -> Client:
        reader, writer = await asyncio.open_connection(
            Client.HOSTNAME,
            Client.PORT
        )
        return Client(name, Relay(reader, writer))
    

    ### METHODS ###
    def close (self):
        self.relay.close()

    def get (self) -> Optional[Message]:
        return self.relay.get()

    def put (self, msg: Message):
        self.relay.put(msg)