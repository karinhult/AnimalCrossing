import numpy as np
import itertools

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

def getRoadWidth(sugarArena, undesirability): # Temporary
    roadCorners = np.array([[dimension[0], dimension[-1]] for dimension in np.where(sugarArena == undesirability)]).T
    roadWidth = np.diff(roadCorners, axis=0)[0][1]+1
    if roadWidth >= np.shape(sugarArena)[0]:
        raise Exception('Horizontal road')
    return roadWidth

class Population:
    def __init__(self, preyAmount, visionRange, metabolismRange, sugarLevelRange, sugarArena, undesirability):
        roadWidth = getRoadWidth(sugarArena, undesirability)
        arenaLength = np.shape(sugarArena)[0]
        positions = np.random.randint((0,0), (arenaLength, arenaLength-roadWidth), (preyAmount, 2))
        positions[:,1] = positions[:,1] + roadWidth*(positions[:,1] >= (arenaLength-roadWidth)/2)

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

    def updateSugarLevels(self, sugarArena):
        pos = self.positions
        sugarInCells = sugarArena[pos[:,0], pos[:,1]]
        self.sugarLevels = self.sugarLevels + sugarInCells - self.metabolisms

    def moveNotSugar(self, agent, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax):
        L = np.shape(sugarArena)[0]
        notValidPosition = True
        while notValidPosition:
            v = np.random.uniform(0, agent.vision)
            theta = np.random.uniform(0, 2 * np.pi)
            velocity = np.array([np.rint(v * np.sin(theta)), np.rint(v * np.cos(theta))]).flatten()
            newPosition = agent.position + velocity
            insideArena = newPosition[0] >= 0 and newPosition[0] < L and newPosition[1] >= 0 and newPosition[1] < L
            validVelocity = np.linalg.norm(velocity, axis=0) <= agent.vision
            if insideArena and validVelocity:
                notOnRoad = sugarArena[int(newPosition[0]), int(newPosition[1])] != -2
                if len(crossingMin) != 0 and len(crossingMax) != 0 and notOnRoad:
                    distanceCrossingMin = np.linalg.norm(agent.position - crossingMin[:, :], axis=1)
                    distanceCrossingMax = np.linalg.norm(agent.position - crossingMax[:, :], axis=1)
                    if ((distanceCrossingMin <= agent.vision).any() or (distanceCrossingMax <= agent.vision).any()):
                        return newPosition
                if notOnRoad and (np.sign(newPosition[1] - iRoadMin) == np.sign(agent.position[1] - iRoadMin)
                                or np.sign(newPosition[1] - iRoadMax) == np.sign(agent.position[1] - iRoadMax)):
                    return newPosition

    def chooseRoad(self, agent, localSugarList, crossingMin, crossingMax, iRoadMin, iRoadMax, probCross):
        positionChoice = -1
        if len(crossingMin) != 0 and len(crossingMax) != 0:
            distanceCrossingMin = np.linalg.norm(agent.position - crossingMin[:, :], axis=1)
            distanceCrossingMax = np.linalg.norm(agent.position - crossingMax[:, :], axis=1)
            if (distanceCrossingMin <= agent.vision).any() or (distanceCrossingMax <= agent.vision).any():
                iSameSideMin = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(agent.position[1] - iRoadMin))[0]
                iSameSideMax = np.where(np.sign(localSugarList[:, 1] - iRoadMax) == np.sign(agent.position[1] - iRoadMax))[0]
                iSameSide = np.intersect1d(iSameSideMin, iSameSideMax)
                pSameSide = (1-probCross)*np.full_like(iSameSide, 1)
                iBridge = np.setxor1d(iSameSideMin, iSameSideMax)
                pBridge = probCross*np.full_like(iBridge, 1)
                iDiffSideMin = np.where(np.sign(localSugarList[:, 1] - iRoadMin) != np.sign(agent.position[1] - iRoadMin))[0]
                iDiffSideMax = np.where(np.sign(localSugarList[:, 1] - iRoadMax) != np.sign(agent.position[1] - iRoadMax))[0]
                iDiffSide = np.intersect1d(iDiffSideMin, iDiffSideMax)
                pDiffSide = probCross**np.full_like(iDiffSide, 1)

                iLocalSugarList = np.array([])
                possibilities = np.array([])
                iLocalSugarList = np.append(iLocalSugarList, (iSameSide, iBridge, iDiffSide))
                possibilities = np.append(possibilities, (pSameSide, pBridge, pDiffSide)) / np.sum(possibilities)

                positionChoice = np.random.choice(iLocalSugarList, 1, p=possibilities)[0]
            else:
                iLocalSugarList = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(agent.position[1] - iRoadMin))[0]
                nSugarPossibilities = iLocalSugarList.shape[0]
                if nSugarPossibilities > 0:
                    positionChoice = np.random.choice(iLocalSugarList)
        else:
            iLocalSugarList = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(agent.position[1] - iRoadMin))[0]
            nSugarPossibilities = len(iLocalSugarList)
            if nSugarPossibilities > 0:
                positionChoice = np.random.choice(iLocalSugarList)

        return positionChoice

    def updatePositions(self, sugarArena, hasRoad = False, crossingMin = np.array([]), crossingMax = np.array([]),
                        iRoadMin = 0, iRoadMax = 0, probCross = 0.1):
        L = np.shape(sugarArena)[0]
        globalSugarList = np.array(np.where(sugarArena > 0)).T
        for agent in np.random.permutation(self.prey):
            distance = np.linalg.norm(agent.position - globalSugarList[:,:], axis=1)
            iGlobalSugarList = np.where(distance <= agent.vision)[0]
            nSugarPossibilities = len(iGlobalSugarList)
            if nSugarPossibilities > 0:
                if hasRoad:
                    localSugarList = globalSugarList[iGlobalSugarList, :]
                    positionChoice = self.chooseRoad(agent, localSugarList, crossingMin, crossingMax,
                                                iRoadMin, iRoadMax, probCross)
                    if positionChoice == -1:
                        agent.position = self.moveNotSugar(agent, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax).astype(int)
                    else:
                        agent.position = localSugarList[int(positionChoice), :].astype(int)
                        wheres = np.where((globalSugarList[:,:] == localSugarList[int(positionChoice),:]).all(axis=1))[0]
                        globalSugarList = np.delete(globalSugarList, wheres, axis=0)

                else:
                    positionChoice = np.random.choice(iGlobalSugarList)
                    agent.position = globalSugarList[positionChoice,:].astype(int)
                    globalSugarList = np.delete(globalSugarList, positionChoice, axis=0)
            else:
                agent.position = self.moveNotSugar(agent, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax).astype(int)


        self.updateSugarLevels(sugarArena)

    # Animals can give birth on the road
    def reproduce(self, L, vRange, mRange, sRange, reproductionProbability):
        reproductions = (np.random.rand(len(self.visions)) < reproductionProbability)
        reproductionAmount = np.sum(reproductions)
        reproductionPositions = self.positions[reproductions]
        translations = np.array(list(itertools.product(range(-1,2), repeat=2)))
        if reproductionAmount > 0:
            adjacencies = list(np.apply_along_axis(np.add, 1, reproductionPositions, translations))
            positions = np.empty((0,2), int)
            for individualAdjacencies in adjacencies:
                inRange = np.all((individualAdjacencies < L) & (individualAdjacencies >= 0), axis=1)
                individualAdjacencies = individualAdjacencies[inRange]
                posList = [position for position in self.positions]
                individualAdjacencies = [reprPos for reprPos in individualAdjacencies.tolist() if reprPos not in self.positions.tolist()]
                chosenSpot = np.array(individualAdjacencies[np.random.randint(len(individualAdjacencies))])
                positions = np.append(positions, chosenSpot[np.newaxis,:], axis=0)
                if chosenSpot.size == 0:
                    reproductionAmount -= 1
            visions = np.random.randint(vRange[0], vRange[1]+1, reproductionAmount)
            metabolisms = np.random.randint(mRange[0], mRange[1]+1, reproductionAmount)
            sugarLevels = np.random.randint(sRange[0], sRange[1]+1, reproductionAmount)

        babies = np.array([Prey(visions[i].item(), metabolisms[i], sugarLevels[i], positions[i,:]) for i in range(reproductionAmount)])

        self.prey = np.append(self.prey, babies)