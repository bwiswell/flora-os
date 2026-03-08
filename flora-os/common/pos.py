import seared as s


@s.seared
class Pos(s.Seared):

    x: float = s.Float(required=True)
    y: float = s.Float(required=True)

    def __init__ (self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y