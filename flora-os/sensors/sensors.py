from __future__ import annotations

from ..controller import Controller
from ..network import Client, Message, MessageType

from .mouth import Mouth


class Sensors(Controller):

    def __init__ (self, client: Client):
        Controller.__init__(self, client)
        self.mouth = Mouth()


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Sensors:
        client = await Client.connect('sensors')
        return Sensors(client)
    

    ### METHODS ###
    def handle_message (self, msg: Message):
        print(f'handling {msg.type}...')
        if msg.type == MessageType.EXIT:
            self.running = False
        elif msg.type == MessageType.MOUTH:
            self.mouth.update(*Message.decode_mouth(msg))

    async def update (self):
        pass