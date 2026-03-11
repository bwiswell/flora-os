from __future__ import annotations

from ..controller import Controller
from ..network import Client, Message, MessageType

from .head import Head
from .mouth import Mouth
from .sonar import Sonar


class Sensors(Controller):

    def __init__ (self, client: Client):
        Controller.__init__(self, client)
        self.head = Head()
        self.mouth = Mouth()
        self.sonar = Sonar(self.mouth)


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Sensors:
        client = await Client.connect('sensors')
        return Sensors(client)
    

    ### METHODS ###
    async def handle_message (self, msg: Message):
        print(f'handling {msg.type}...')
        if msg.type == MessageType.EXIT:
            self.running = False
        elif msg.type == MessageType.LOOK:
            self.head.update(*Message.decode_look(msg))
        elif msg.type == MessageType.MOUTH:
            self.mouth.update(*Message.decode_mouth(msg))
        elif msg.type == MessageType.SCAN:
            scan = await self.sonar.scan()
            await self.send(Message.sonar(scan))

    async def setup (self):
        pass

    async def update (self):
        pass