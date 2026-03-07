from ..common import FineMotor
from ..util import clip


class Head:

    MAX_SWIVEL = 60
    MAX_TILT = 45
    MIN_SWIVEL = -60
    MIN_TILT = -45
    SWIVEL_PORT = 'A'
    TILT_PORT = 'A'

    def __init__ (self):
        self.swivel = FineMotor(Head.SWIVEL_PORT, plimit = 0.7)
        self.tilt = FineMotor(Head.TILT_PORT, plimit = 0.7)

    
    ### METHODS ###
    def update (self, swivel: int, tilt: int):
        self.swivel.run_to_position(
            clip(swivel, Head.MIN_SWIVEL, Head.MAX_SWIVEL),
            blocking = False,
            speed_limit = 50
        )
        self.tilt.run_to_position(
            clip(tilt, Head.MIN_TILT, Head.MAX_TILT),
            blocking = False,
            speed_limit = 50
        )