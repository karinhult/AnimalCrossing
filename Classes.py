class Prey:
    def __init__(self, vision, metabolism, sugarLevel, pos):
        self.vision = vision
        self.metab = metabolism
        self.food = sugarLevel
        self.pos = pos

    def getVision(self):
        return self.vision

    def eat(self, food):
        self.food = self.food + food - self.metab
        return self.food

    def setPos(self, x):
        self.pos = x

    def getPos(self):
        return self.Pos