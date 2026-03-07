from __future__ import annotations

from ..controller import Controller
from ..network import Message, MessageType, Server


class Flora(Controller):

    def __init__ (self, server: Server):
        Controller.__init__(self, server)


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Flora:
        server = await Server.connect('flora')
        return Flora(server)
    

    ### METHODS ###
    def handle_message (self, msg: Message):
        print(f'handling {msg.type}...')

    async def update (self):
        pass