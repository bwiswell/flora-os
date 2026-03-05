from __future__ import annotations

from typing import Optional

from .message import Message


class IO:
    
    PORT = '25565'

    def __init__ (self, name: str):
        self.name = name

    
    ### CLASS METHODS ###
    @classmethod
    async def connect (cls, name: str) -> IO:
        raise NotImplementedError
    

    ### METHODS ###
    async def close (self):
        raise NotImplementedError

    async def get (self) -> Optional[Message]:
        raise NotImplementedError

    async def put (self, msg: Message):
        raise NotImplementedError