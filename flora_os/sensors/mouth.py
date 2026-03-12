from buildhat import Matrix

from ..common import Expression, Mood, EXPRESSIONS


class Mouth:
    
    PORT = 'A'

    def __init__ (self):
        self.matrix = Matrix(Mouth.PORT)
        self.initialize()


    ### METHODS ###
    def initialize (self):
        self.update(Expression.FLAT, Mood.NONE)

    def ready (self):
        self.update(Expression.RESTING, Mood.CALM)

    def sonar (self, idx: int):
        if idx % 2 == 0:
            self.update(Expression.OPEN, Mood.CURIOUS)
        else:
            self.update(Expression.CORNERS, Mood.CURIOUS)

    def update (self, expression: Expression, mood: Mood):
        self.expression = expression
        self.mood = mood
        pattern = EXPRESSIONS[expression]
        matrix = [
            [(mood.value if val else 0, 10) for val in row]
            for row in pattern
        ]
        self.matrix.set_pixels(matrix)