from buildhat import Matrix

from ..common import Expression, Mood, EXPRESSIONS


class Mouth:
    
    PORT = 'A'

    def __init__ (self):
        self.matrix = Matrix(Mouth.PORT)
        self.update(Expression.RESTING, Mood.NONE)


    ### METHODS ###
    def update (self, expression: Expression, mood: Mood):
        pattern = EXPRESSIONS[expression]
        matrix = [
            [(mood.value if val else 0, 10) for val in row]
            for row in pattern
        ]
        self.matrix.set_pixels(matrix)