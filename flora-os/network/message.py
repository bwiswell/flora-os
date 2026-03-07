from __future__ import annotations

from enum import Enum
import json

from ..common import Expression, Mood


class MessageType(Enum):
    PING = 0
    PONG = 1
    INIT = 2
    EXIT = 3
    MOVE = 4
    STOP = 5
    LOOK = 6
    MOUTH = 7
    SCAN = 8
    SONAR = 9


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
    def decode_look (cls, msg: Message) -> tuple[int, int]:
        stringified = msg.payload.decode('utf-8')
        data = json.loads(stringified)
        return data['swivel'], data['tilt']

    @classmethod
    def decode_mouth (cls, msg: Message) -> tuple[Expression, Mood]:
        stringified = msg.payload.decode('utf-8')
        data = json.loads(stringified)
        return Expression(data['expression']), Mood(data['mood'])

    @classmethod
    def decode_move (cls, msg: Message) -> tuple[float, float]:
        stringified = msg.payload.decode('utf-8')
        data = json.loads(stringified)
        return data['dl'], data['dr']
    
    @classmethod
    def decode_sonar (
                cls,
                msg: Message
            ) -> tuple[list[int], list[float], list[float]]:
        stringified = msg.payload.decode('utf-8')
        data = json.loads(stringified)
        return data['angles'], data['left'], data['right']
    
    @classmethod
    def exit (cls, dest: str) -> Message:
        return Message(MessageType.EXIT, 'flora', dest)
    
    @classmethod
    def init (cls, name: str) -> Message:
        return Message(MessageType.INIT, name)
    
    @classmethod
    def look (cls, swivel: int, tilt: int) -> Message:
        data = { 'swivel': swivel, 'tilt': tilt }
        stringified = json.dumps(data)
        return Message(
            MessageType.LOOK,
            src = 'flora',
            dest = 'sensors',
            payload = stringified.encode('utf-8')
        )
    
    @classmethod
    def mouth (cls, expression: Expression, mood: Mood) -> Message:
        data = { 'expression': expression.value, 'mood': mood.value }
        stringified = json.dumps(data)
        return Message(
            MessageType.MOUTH,
            src = 'flora',
            dest = 'sensors',
            payload = stringified.encode('utf-8')
        )

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
    def scan (cls) -> Message:
        return Message(MessageType.SCAN, 'flora', 'sensors')
    
    @classmethod
    def sonar (
                cls,
                angles: list[int],
                left: list[float],
                right: list[float]
            ) -> Message:
        data = { 'angles': angles, 'left': left, 'right': right }
        stringified = json.dumps(data)
        return Message(
            MessageType.SONAR,
            src = 'sensors',
            dest = 'flora',
            payload = stringified.encode('utf-8')
        )
    
    @classmethod
    def stop (cls) -> Message:
        return Message(MessageType.STOP, 'flora', 'traction')