from __future__ import annotations

from enum import Enum
import json


class MessageType(Enum):
    PING = 0
    PONG = 1
    INIT = 2
    EXIT = 3
    MOVE = 4
    STOP = 5


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


    ### CLASS METHODS ###
    @classmethod
    def decode_move (cls, msg: Message) -> tuple[float, float]:
        stringified = msg.payload.decode('utf-8')
        data = json.loads(stringified)
        return data['dl'], data['dr']
    
    @classmethod
    def exit (cls, dest: str) -> Message:
        return Message(MessageType.EXIT, 'flora', dest)
    
    @classmethod
    def init (cls, name: str) -> Message:
        return Message(MessageType.INIT, name)

    @classmethod
    def move (cls, dl: float, dr: float) -> Message:
        data = { 'dl': dl, 'dr': dr }
        stringified = json.dumps(data)
        return Message(
            MessageType.MOVE,
            src = 'flora',
            dest = 'traction',
            payload = stringified.encode('utf-8')
        )
    
    @classmethod
    def stop (cls) -> Message:
        return Message(MessageType.STOP, 'flora', 'traction')