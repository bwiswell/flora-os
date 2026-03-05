from enum import Enum


class MessageType(Enum):
    OTHER = 0


class Message:

    NEXT_ID = 0

    def __init__ (self, type: MessageType, payload: bytes):
        self.id = Message.NEXT_ID
        Message.NEXT_ID += 1
        self.type = type
        self.payload = payload