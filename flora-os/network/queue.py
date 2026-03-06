from asyncio import Lock, Queue as AQueue

from .message import Message


class Queue:

    def __init__ (self):
        self.in_lock = Lock()
        self.incoming = AQueue()
        self.out_lock = Lock()
        self.outgoing = AQueue()

    
    ### PROPERTIES ###
    @property
    def is_incoming (self) -> bool:
        return self.incoming.qsize() > 0
    
    @property
    def is_outgoing (self) -> bool:
        return self.outgoing.qsize() > 0
    

    ### METHODS ###
    async def get_incoming (self) -> Message:
        await self.in_lock.acquire()
        incoming: Message = await self.incoming.get()
        self.in_lock.release()
        print(f'found {incoming.type} in queue')
        return incoming
    
    async def get_outgoing (self) -> Message:
        await self.out_lock.acquire()
        outgoing = await self.outgoing.get()
        self.out_lock.release()
        return outgoing
    
    async def put_incoming (self, msg: Message):
        print(f'putting {msg.type} in incoming queue...')
        await self.in_lock.acquire()
        await self.incoming.put(msg)
        self.in_lock.release()
        
    async def put_outgoing (self, msg: Message):
        await self.out_lock.acquire()
        await self.outgoing.put(msg)
        self.out_lock.release()