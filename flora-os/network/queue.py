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


    ### PROPERTIES ###
    @property
    def is_incoming (self) -> bool:
        print(f'{self.incoming.qsize()} in incoming queue')
        return self.incoming.qsize() > 0
    
    @property
    def is_outgoing (self) -> bool:
        return self.outgoing.qsize() > 0
    

    ### METHODS ###
    def get_incoming (self) -> Optional[Message]:
        incoming: Optional[Message] = None
        if self.is_incoming:
            print('trying to get message from incoming queue...')
            self.in_lock.acquire()
            incoming = self.incoming.get()
            print(f'found {incoming.type} in queue')
            self.in_lock.release()
        return incoming
    
    def get_outgoing (self) -> Optional[Message]:
        outgoing: Optional[Message] = None
        if self.is_outgoing:
            print('trying to get message from outgoing queue...')
            self.out_lock.acquire()
            outgoing = self.outgoing.get()
            print(f'found {outgoing.type} in queue')
            self.out_lock.release()
        return outgoing
    
    def put_incoming (self, msg: Message):
        print(f'putting {msg.type} in incoming queue...')
        self.in_lock.acquire()
        self.incoming.put(msg)
        self.in_lock.release()
        print(f'incoming queue size is now {self.incoming.qsize()}')
        
    def put_outgoing (self, msg: Message):
        self.out_lock.acquire()
        self.outgoing.put(msg)
        self.out_lock.release()