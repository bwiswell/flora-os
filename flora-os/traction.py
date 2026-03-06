from buildhat import Motor

from .controller import Controller
from .network import Client, Message, MessageType
from .util import clip_and_scale


class Traction(Controller):

    FL = 'A'
    FR = 'B'
    MAX_SPEED = 100
    RL = 'C'
    RR = 'D'

    def __init__ (self, client: Client):
        Controller.__init__(self, client)
        self.fl = Motor(Traction.FL)
        self.fr = Motor(Traction.FR)
        self.rl = Motor(Traction.RL)
        self.rr = Motor(Traction.RR)


    ### CLASS METHODS ###
    @classmethod
    async def initialize (cls) -> Controller:
        client = await Client.connect('traction')
        return Controller(client)
    

    ### METHODS ###
    def handle_message (self, msg: Message):
        super().handle_message(msg)
        if msg.type == MessageType.MOVE:
            self.handle_move(*Message.decode_move(msg))
        elif msg.type == MessageType.STOP:
            self.handle_stop()

    def handle_move (self, dl: float, dr: float):
        l = clip_and_scale(dl, 100, -Traction.MAX_SPEED, Traction.MAX_SPEED)
        r = clip_and_scale(dr, 100, -Traction.MAX_SPEED, Traction.MAX_SPEED)
        self.fl.start(l)
        self.fr.start(r)
        self.rl.start(l)
        self.rr.start(r)

    def handle_stop (self):
        self.fl.stop()
        self.fr.stop()
        self.rl.stop()
        self.rr.stop()

    async def update (self):
        pass