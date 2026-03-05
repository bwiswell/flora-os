from enum import Enum


class MessageType(Enum):
    PING = 0
    PONG = 1
    INIT = 2
    EXIT = 3


class Message:

    NEXT_ID = 0

    def __init__ (
                self,
                type: MessageType,
                src: str,
                dest: str = 'flora',
                payload: bytes = bytes()
            ):
        self.id = Message.NEXT_ID
        Message.NEXT_ID += 1
        self.type = type
        self.src = src
        self.dest = dest
        self.payload = payload