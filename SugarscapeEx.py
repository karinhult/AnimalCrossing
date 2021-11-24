import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
from copy import deepcopy
import time
import random as rnd
import itertools

def updateSugarArena(L, positions, sugarArena, growthRate, sproutRate, sugar_max, roadWidth=4, roadValue=-1):
    sugarArena_updated = deepcopy(sugarArena)
    nNewSugarPoints = np.random.poisson(sproutRate)
    newSugarPositions = np.random.randint(0, L, size=[nNewSugarPoints, 2])

    sugarArena_updated[newSugarPositions[:,0], newSugarPositions[:,1]] += growthRate

    sugarArena_updated = np.minimum(sugarArena_updated, sugar_max)

    sugarArena_updated[positions[:,0], positions[:,1]] = 0
    sugarArena_updated = addRoad(L/2, roadWidth, sugarArena_updated, roadValue)
    return sugarArena_updated

def updateSugarLevels(positions, sugarlevels, metabolisms, visions, sugarArena):
    sugarLevels_updated = np.copy(sugarlevels)
    sugarInCell = (sugarArena[positions[:,0], positions[:,1]])[:,np.newaxis]
    sugarLevels_updated += sugarInCell - metabolisms
    survivors = np.where(sugarLevels_updated > 0)[0]
    return positions[survivors,:], visions[survivors], metabolisms[survivors], sugarLevels_updated[survivors]

def moveNotSugar(positions, visions, a, L, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax):
    notValidPosition = True
    while notValidPosition:
        v = np.random.uniform(0, visions[a])
        theta = np.random.uniform(0, 2 * np.pi)
        velocity = np.array([np.rint(v * np.sin(theta)), np.rint(v * np.cos(theta))]).flatten()
        newPosition = positions[a, :] + velocity
        insideArena = newPosition[0] >= 0 and newPosition[0] < L and newPosition[1] >= 0 and newPosition[1] < L
        validVelocity = np.linalg.norm(velocity, axis=0) <= visions[a]
        if insideArena and validVelocity:
            notOnRoad = sugarArena[int(newPosition[0]), int(newPosition[1])] != -2
            if len(crossingMin) != 0 and len(crossingMax) != 0 and notOnRoad:
                distanceCrossingMin = np.linalg.norm(positions[a, :] - crossingMin[:, :], axis=1)
                distanceCrossingMax = np.linalg.norm(positions[a, :] - crossingMax[:, :], axis=1)
                if ((distanceCrossingMin <= visions[a]).any() or (distanceCrossingMax <= visions[a]).any()):
                    return newPosition
            if notOnRoad and (np.sign(newPosition[1] - iRoadMin) == np.sign(positions[a,1] - iRoadMin)
                              or np.sign(newPosition[1] - iRoadMax) == np.sign(positions[a,1] - iRoadMax)):
                return newPosition

def chooseRoad(positions, visions, a, localSugarList, crossingMin, crossingMax, iRoadMin, iRoadMax, probCross):
    positionChoice = -1
    if len(crossingMin) != 0 and len(crossingMax) != 0:
        distanceCrossingMin = np.linalg.norm(positions[a, :] - crossingMin[:, :], axis=1)
        distanceCrossingMax = np.linalg.norm(positions[a, :] - crossingMax[:, :], axis=1)
        if (distanceCrossingMin <= visions[a]).any() or (distanceCrossingMax <= visions[a]).any():
            iSameSideMin = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(positions[a, 1] - iRoadMin))[0]
            iSameSideMax = np.where(np.sign(localSugarList[:, 1] - iRoadMax) == np.sign(positions[a, 1] - iRoadMax))[0]
            iSameSide = np.intersect1d(iSameSideMin, iSameSideMax)
            pSameSide = (1-probCross)*np.full_like(iSameSide, 1)
            iBridge = np.setxor1d(iSameSideMin, iSameSideMax)
            pBridge = probCross*np.full_like(iBridge, 1)
            iDiffSideMin = np.where(np.sign(localSugarList[:, 1] - iRoadMin) != np.sign(positions[a, 1] - iRoadMin))[0]
            iDiffSideMax = np.where(np.sign(localSugarList[:, 1] - iRoadMax) != np.sign(positions[a, 1] - iRoadMax))[0]
            iDiffSide = np.intersect1d(iDiffSideMin, iDiffSideMax)
            pDiffSide = probCross**np.full_like(iDiffSide, 1)

            iLocalSugarList = np.array([])
            possibilities = np.array([])
            iLocalSugarList = np.append(iLocalSugarList, iSameSide)
            possibilities = np.append(possibilities, pSameSide)
            iLocalSugarList = np.append(iLocalSugarList, iBridge)
            possibilities = np.append(possibilities, pBridge)
            iLocalSugarList = np.append(iLocalSugarList, iDiffSide)
            possibilities = np.append(possibilities, pDiffSide)
            possibilities = possibilities/np.sum(possibilities)

            positionChoice = np.random.choice(iLocalSugarList, 1, p=possibilities)[0]
        else:
            iLocalSugarList = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(positions[a, 1] - iRoadMin))[0]
            nSugarPossibilities = iLocalSugarList.shape[0]
            if nSugarPossibilities > 0:
                positionChoice = rnd.choice(iLocalSugarList)
    else:
        iLocalSugarList = np.where(np.sign(localSugarList[:, 1] - iRoadMin) == np.sign(positions[a, 1] - iRoadMin))[0]
        nSugarPossibilities = len(iLocalSugarList)
        if nSugarPossibilities > 0:
            positionChoice = rnd.choice(iLocalSugarList)

    return positionChoice

def updatePositions(A, L, positions, visions, sugarArena, hasRoad = False, crossingMin = np.array([]), crossingMax = np.array([]),
                    iRoadMin = 0, iRoadMax = 0, probCross = 0.1):
    positions_updated = np.copy(positions)
    globalSugarList = np.array(np.where(sugarArena > 0)).T
    for a in rnd.sample(range(A), A):
        distance = np.linalg.norm(positions[a,:] - globalSugarList[:,:], axis=1)
        iGlobalSugarList = np.where(distance <= visions[a])[0]
        nSugarPossibilities = len(iGlobalSugarList)
        if nSugarPossibilities > 0:
            if hasRoad:
                localSugarList = globalSugarList[iGlobalSugarList, :]
                positionChoice = chooseRoad(positions, visions, a, localSugarList, crossingMin, crossingMax,
                                            iRoadMin, iRoadMax, probCross)
                if positionChoice == -1:
                    positions_updated[a,:] = moveNotSugar(positions, visions, a, L, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax)
                else:
                    positions_updated[a,:] = localSugarList[int(positionChoice), :]
                    wheres = np.where((globalSugarList[:,:] == localSugarList[int(positionChoice),:]).all(axis=1))[0]
                    globalSugarList = np.delete(globalSugarList, wheres, axis=0)

            else:
                positionChoice = rnd.choice(iGlobalSugarList)
                positions_updated[a,:] = globalSugarList[positionChoice,:]
                globalSugarList = np.delete(globalSugarList, positionChoice, axis=0)
        else:
            positions_updated[a,:] = moveNotSugar(positions, visions, a, L, sugarArena, iRoadMin, iRoadMax, crossingMin, crossingMax)

    return positions_updated

def initializeSugarArena(L, plantProb, globalSugarMax, hasRoad = False, roadWidth=4, roadValue=-2):
    # For later: Add different sugar maximums in different parts of the arena?
    sugarArena = np.random.randint(1,globalSugarMax, size=(L,L)) * (np.random.rand(L,L) < plantProb)
    if hasRoad:
        sugarArena = addRoad(L/2, roadWidth, sugarArena, roadValue)
    return sugarArena

#Adds road
def addRoad(pos, width, sugarArena, undesirability = -1):
    j1 = int(pos-width/2)
    j2 = int(pos+width/2)
    sugarArena[:, j1:j2] = undesirability
    return sugarArena

def initializePrey(A, L, v_min, v_max, m_min, m_max, s_min, s_max, hasRoad = False, roadWidth=4, oneSide=True):
    if hasRoad:
        positions = np.random.randint(0, [L, int(L/2-roadWidth)], (A, 2))
    else:
        positions = np.random.randint(0, [L, L], (A, 2))
    visions = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)

    #preys = [Prey(visions[i], metabolisms[i], sugarlevels[i], positions[i]) for i in range(A)]
    #can return prey and positions? if we want that
    return positions, visions, metabolisms, sugarlevels

# Animals can give birth on the road
def reproduce(L, v_min, v_max, m_min, m_max, s_min, s_max, positions, visions, metabolisms, sugarlevels, reproductionProbability):
    reproductions = (np.random.rand(len(visions)) < reproductionProbability)
    reproductionAmount = np.sum(reproductions)
    reproductionPositions = positions[reproductions]
    translations = np.array(list(itertools.product(range(-1,2), repeat=2)))
    if reproductionAmount > 0:
        adjacencies = list(np.apply_along_axis(np.add, 1, reproductionPositions, translations))
        for individualAdjacencies in adjacencies:
            inRange = np.all(individualAdjacencies < L, axis=1)
            individualAdjacencies = individualAdjacencies[inRange]
            posList = [position for position in positions]
            individualAdjacencies = [reprPos for reprPos in individualAdjacencies.tolist() if reprPos not in positions.tolist()]
            chosenSpot = np.array(individualAdjacencies[np.random.randint(len(individualAdjacencies))])
            positions = np.append(positions, chosenSpot[np.newaxis,:], axis=0)
            if chosenSpot.size == 0:
                reproductionAmount -= 1
        visions = np.append(visions, np.random.randint(v_min, v_max+1, (reproductionAmount, 1)), axis=0)
        metabolisms = np.append(metabolisms, np.random.randint(m_min, m_max+1, (reproductionAmount, 1)), axis=0)
        sugarlevels = np.append(sugarlevels, np.random.randint(s_min, s_max+1, (reproductionAmount, 1)), axis=0)

    return positions, visions, metabolisms, sugarlevels

def getImage(positions, sugarArena, A, globalSugarMax):
    width = np.shape(sugarArena)[0]
    image = np.zeros((width, width, 3))
    image[:,:,1] = 175 # Green grass
    image[sugarArena > 0, :] = 0
    image[:,:,0] = (sugarArena * 1.5*255/globalSugarMax).astype(int) # Red food
    image[sugarArena < 0, :] = 75
    for a in range(A):
        image[int(positions[a,0]), int(positions[a,1]), :] = 255 # White agents
    # breakpoint()
    return image

imageDelay = 0.2
def changeImageDelay(increase=True):
    global imageDelay
    if increase:
        if imageDelay == 0.01:
            imageDelay = 0.1
        else:
            imageDelay += 0.1
    else:
        imageDelay = max(0.01, imageDelay-0.1)
    currentDelay.delete('1.0', 'end')
    currentDelay.insert(END, f'Current delay: {"{0:.2g}".format(imageDelay)}')
    currentDelay.tag_add("center", "1.0", "end")

res = 500  # Animation resolution
tk = Tk()
tk.geometry(str(int(res * 1.1)) + 'x' + str(int(res * 1.3)))
tk.configure(background='white')

canvas = Canvas(tk, bd=2)  # Generate animation window
tk.attributes('-topmost', 0)
canvas.place(x=res / 20, y=res / 20, height=res, width=res)
ccolor = ['#0008FF', '#DB0000', '#12F200']

currentDelay = Text(tk)
currentDelay.tag_configure("center", justify='center')
currentDelay.insert('1.0', f'Current delay: {imageDelay}')
currentDelay.tag_add("center", "1.0", "end")
currentDelay.place(relx=0.05, rely=.81, relheight=0.04, relwidth=0.3)
speedUp = Button(tk, text='Speed up', command=lambda: changeImageDelay(False))
speedUp.place(relx=0.05, rely=.85, relheight=0.12, relwidth=0.15)
speedDn = Button(tk, text='Speed down', command=changeImageDelay)
speedDn.place(relx=0.2, rely=.85, relheight=0.12, relwidth=0.15)

plantProb = 0.5
L = 50
A = 100
A_list = [A]
globalSugarMax = 4
v_min = 1
v_max = 6
m_min = 1
m_max = 4
s_min = 5
s_max = 25
growthRate = 1
sproutRate = 25
reproductionProbability = 0.1
roadWidth = 4
roadValue = -2

sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax, hasRoad = True, roadWidth = roadWidth, roadValue = roadValue)
sugar_max = np.ones([L,L])*globalSugarMax
sugarArena_t = deepcopy(sugarArena_0)
positions_0, visions, metabolisms, sugarlevels_0 = initializePrey(A, L, v_min, v_max, m_min, m_max, s_min, s_max, hasRoad = True)

positions_t = deepcopy(positions_0)
sugarlevels_t = deepcopy(sugarlevels_0)

t = 0

image = getImage(positions_t, sugarArena_t, A, globalSugarMax)
img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
canvas.create_image(0, 0, anchor=NW, image=img)
tk.title('time=' + str(t) + ', alive agents=' + str(int(A)))
time.sleep(imageDelay)
tk.update()

for t in range(1,500):
    positions_t = updatePositions(A, L, positions_t, visions, sugarArena_t, hasRoad = True, iRoadMin = np.rint((L-4)/2),
                                  iRoadMax = np.rint((L+4)/2))
    positions_t, visions, metabolisms, sugarlevels_t = updateSugarLevels(positions_t, sugarlevels_t, metabolisms, visions, sugarArena_t)
    positions_t, visions, metabolisms, sugarlevels_t = reproduce(L, v_min, v_max, m_min, m_max, s_min, s_max, positions_t, visions, metabolisms, sugarlevels_t, reproductionProbability)
    A = len(sugarlevels_t)
    A_list.append(A)
    
    image = getImage(positions_t, sugarArena_t, A, globalSugarMax)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title('time=' + str(t) + ', alive agents=' + str(int(A)))
    time.sleep(imageDelay)
    tk.update()
    
    sugarArena_t = updateSugarArena(L, positions_t, sugarArena_t, growthRate, sproutRate, sugar_max, roadWidth, roadValue)

Tk.mainloop(canvas)

# plt.plot(A_list)
# plt.show()

#'''