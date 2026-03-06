from buildhat import Motor



class Sonar:

    PORT = 'A'

    def __init__ (self):
        self.motor = Motor(Sonar.PORT)