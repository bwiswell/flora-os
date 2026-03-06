from buildhat import Motor

from ..util import clip


class Head:

    MAX_SWIVEL = 60
    MAX_TILT = 45
    MIN_SWIVEL = -60
    MIN_TILT = -45
    SWIVEL_PORT = 'A'
    TILT_PORT = 'A'

    def __init__ (self):
        self.swivel = Motor(Head.SWIVEL_PORT)
        self.tilt = Motor(Head.TILT_PORT)

    
    ### METHODS ###
    def update (self, swivel: int, tilt: int):
        self.swivel.run_to_position(
            clip(swivel, Head.MIN_SWIVEL, Head.MAX_SWIVEL),
            speed = 60,
            blocking = False
        )
        self.tilt.run_to_position(
            clip(swivel, Head.MIN_TILT, Head.MAX_TILT),
            speed = 60,
            blocking = False
        )