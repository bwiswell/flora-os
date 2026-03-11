import seared as s


@s.seared
class Scan(s.Seared):

    angles: list[float] = s.Float(many=True, required=True)
    left: list[float] = s.Float(many=True, required=True)
    right: list[float] = s.Float(many=True, required=True)

    def __init__ (
                self,
                angles: list[float],
                left: list[float],
                right: list[float]
            ):
        self.angles = angles
        self.left = left
        self.right = right