import asyncio
import pickle
from threading import Thread
from typing import Optional

from .message import Message
from .queue import Queue


class Relay(Thread):

    READ_SIZE = 20000
    READ_TIMEOUT = 1

    def __init__ (
                self, 
                reader: asyncio.StreamReader, 
                writer: asyncio.StreamWriter
            ):
        Thread.__init__(self, target=self._start_relay)
        self.queue = Queue()
        self.reader = reader
        self.running = True
        self.writer = writer

    
    ### HELPERS ###
    async def _read (self) -> Optional[Message]:
        try:
            data = await asyncio.wait_for(
                self.reader.read(Relay.READ_SIZE),
                Relay.READ_TIMEOUT
            )
            return pickle.loads(data)
        except:
            return None
        
    async def _relay (self):
        while self.running:
            if self.queue.is_outgoing:
                out_msg = self.queue.get_outgoing()
                await self._write(out_msg)
            in_msg = await self._read()
            if in_msg is not None:
                self.queue.put_incoming(in_msg)
            await asyncio.sleep(0.1)
        self.writer.close()

    def _start_relay (self):
        asyncio.run(self._relay())
        
    async def _write (self, msg: Message):
        data = pickle.dumps(msg)
        self.writer.write(data)
        await self.writer.drain()


    ### METHODS ###
    def close (self): 
        self.running = False

    def get (self) -> Optional[Message]:
        if self.queue.is_incoming:
            return self.queue.get_incoming()
        else:
            return None
        
    def put (self, msg: Message):
        self.queue.put_outgoing(msg)

    async def wait_for_get (self) -> Message:
        msg: Optional[Message] = None
        while msg is None:
            msg = await self._read()
        return msg