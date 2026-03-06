import asyncio
import pickle
from typing import Optional

from .message import Message


class Relay:

    READ_SIZE = 20000
    READ_TIMEOUT = 1

    def __init__ (
                self, 
                reader: asyncio.StreamReader, 
                writer: asyncio.StreamWriter
            ):
        self.reader = reader
        self.writer = writer

    
    ### METHODS ###
    async def close (self):
        self.writer.close()
        await self.writer.wait_closed()

    async def read (self) -> Optional[Message]:
        try:
            data = await asyncio.wait_for(
                self.reader.read(Relay.READ_SIZE),
                Relay.READ_TIMEOUT
            )
            msg: Message = pickle.loads(data)
            print(f'received {msg.type}')
            return msg
        except:
            return None

    async def wait_for_get (self) -> Message:
        msg: Optional[Message] = None
        while msg is None:
            msg = await self.read()
        return msg
        
    async def write (self, msg: Message):
        await asyncio.sleep(0.3)
        print(f'writing {msg.type}...')
        data = pickle.dumps(msg)
        self.writer.write(data)
        await self.writer.drain()