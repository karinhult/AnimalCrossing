import numpy as np

class Prey:
    def __init__(self, vision, metabolism, sugarLevel, position):
        self._vision = vision
        self._metabolism = metabolism
        self._sugarLevel = sugarLevel
        self._position = position

    @property
    def vision(self):
        return self._vision
    @property
    def metabolism(self):
        return self._metabolism
    @property
    def sugarLevel(self):
        return self._sugarLevel
    @property
    def position(self):
        return self._position

    @vision.setter
    def vision(self, value):
        self._vision = value
    @metabolism.setter
    def metabolism(self, value):
        self._metabolism = value
    @sugarLevel.setter
    def sugarLevel(self, value):
        self._sugarLevel = value
    @position.setter
    def position(self, value):
        self._position = value

class Population:
    def __init__(self, preyAmount, visionRange, metabolismRange, sugarLevelRange, arenaLength):
        positions =   np.random.randint(0, arenaLength, (preyAmount, 2))
        visions =     np.random.randint(visionRange[0], visionRange[1]+1, preyAmount)
        metabolisms = np.random.randint(metabolismRange[0], metabolismRange[1]+1, preyAmount)
        sugarLevels = np.random.randint(sugarLevelRange[0], sugarLevelRange[1], preyAmount)
        self._prey =  np.array([Prey(visions[i], metabolisms[i], sugarLevels[i], positions[i, :]) for i in range(preyAmount)])

    @property
    def prey(self):
        return self._prey
    @property
    def visions(self):
        return np.array([animal.vision for animal in self._prey])
    @property
    def metabolisms(self):
        return np.array([animal.metabolism for animal in self._prey])
    @property
    def sugarLevels(self):
        return np.array([animal.sugarLevel for animal in self._prey])
    @property
    def positions(self):
        return np.array([animal.position for animal in self._prey])

    @prey.setter
    def prey(self, values):
        self._prey = values
    @visions.setter
    def visions(self, values):
        for animal, vision in zip(self._prey, values):
            animal.vision = vision
    @metabolisms.setter
    def metabolisms(self, values):
        for animal, metabolism in zip(self._prey, values):
            animal.metabolism = metabolism
    @sugarLevels.setter
    def sugarLevels(self, values):
        for animal, sugarLevel in zip(self._prey, values):
            animal.sugarLevel = sugarLevel
        self._prey = self._prey[self.sugarLevels > 0]
    @positions.setter
    def positions(self, values):
        for animal, position in zip(self._prey, values):
            animal.position = position