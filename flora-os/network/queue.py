from queue import Queue as AQueue
from threading import Lock
from typing import Optional

from .message import Message


class Queue:

    def __init__ (self):
        self.in_lock = Lock()
        self.incoming = AQueue()
        self.out_lock = Lock()
        self.outgoing = AQueue()
    

    ### METHODS ###
    async def get_incoming (self) -> Optional[Message]:
        print('trying to get message from incoming queue...')
        await self.in_lock.acquire()
        incoming: Optional[Message] = None
        try:
            incoming = self.incoming.get_nowait()
            print(f'found {incoming.type} in queue')
        except:
            print('incoming queue is empty')
        self.in_lock.release()
        return incoming
    
    async def get_outgoing (self) -> Optional[Message]:
        print('trying to get message from outgoing queue...')
        await self.out_lock.acquire()
        outgoing: Optional[Message] = None
        try:
            outgoing = self.outgoing.get_nowait()
            print(f'found {outgoing.type} in queue')
        except:
            print('outgoing queue is empty')
        self.out_lock.release()
        return outgoing
    
    async def put_incoming (self, msg: Message):
        print(f'putting {msg.type} in incoming queue...')
        await self.in_lock.acquire()
        await self.incoming.put(msg)
        self.in_lock.release()
        print(f'incoming queue size is now {self.incoming.qsize()}')
        
    async def put_outgoing (self, msg: Message):
        await self.out_lock.acquire()
        await self.outgoing.put(msg)
        self.out_lock.release()