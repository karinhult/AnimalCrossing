import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
from copy import deepcopy
import time
import random as rnd
import itertools
from Population import *

def updateSugarArena(N, positions, sugarArena, growthRate, sproutRate, sugar_max):
    sugarArena_updated = deepcopy(sugarArena)
    nNewSugarPoints = np.random.poisson(sproutRate)
    newSugarPositions = np.random.randint(0, N, size=[nNewSugarPoints, 2])

    sugarArena_updated[newSugarPositions[:,0], newSugarPositions[:,1]] += growthRate

    sugarArena_updated = np.minimum(sugarArena_updated, sugar_max)

    sugarArena_updated[positions[:,0], positions[:,1]] = 0
    sugarArena_updated = addRoad(L/2, 4, sugarArena_updated, -1)
    return sugarArena_updated

def updatePositions(A, L, positions, visions, sugarArena):
    positions_updated = np.copy(positions)

    globalSugarList = np.array(np.where(sugarArena != 0)).T
    for a in rnd.sample(range(A), A-1):
        distance = np.linalg.norm(positions[a,:] - globalSugarList[:,:], axis=1)
        iSugarList = np.where(distance <= visions[a])[0]
        nSugarPossibilities = iSugarList.shape[0]
        if nSugarPossibilities > 0:
            positionChoice = rnd.choice(iSugarList)
            positions_updated[a,:] = globalSugarList[positionChoice,:]
            globalSugarList = np.delete(globalSugarList, positionChoice, axis=0)
        else:
            notValidPosition = True
            while notValidPosition:
                v = np.random.uniform(0, visions[a])
                theta = np.random.uniform(0, 2*np.pi)
                vision = np.array([np.rint(v*np.cos(theta)), np.rint(v*np.sin(theta))]).flatten()
                newPosition = positions_updated[a,:] + vision
                insideArena = newPosition[0] >= 0 and newPosition[0] < L and newPosition[1] >= 0 and newPosition[1] < L
                validVision = np.linalg.norm(vision, axis=0) <= visions[a]
                if insideArena and validVision:
                    positions_updated[a, :] = newPosition
                    notValidPosition = False
    return positions_updated

def initializeSugarArena(L, plantProb, globalSugarMax):
    # For later: Add different sugar maximums in different parts of the arena?
    sugarArena = np.random.randint(1,globalSugarMax, size=(L,L)) * (np.random.rand(L,L) < plantProb)
    sugarArena = addRoad(L/2, 4, sugarArena, -1)
    return sugarArena

#Adds road
def addRoad(pos, width, sugarArena, undesirability):
    j1 = int(pos-width/2)
    j2 = int(pos+width/2)
    sugarArena[:,j1:j2] = undesirability
    return sugarArena

def initializePrey(A, N, v_min, v_max, m_min, m_max, s_min, s_max):
    positions = np.random.randint(0, [N, int(N/2-4)], (A, 2))
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
            inRange = np.all((individualAdjacencies < L) & (individualAdjacencies >= 0), axis=1)
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
visionRange = (1, 6)
metabolismRange = (1, 4)
sugarLevelRange = (5, 25)
growthRate = 1
sproutRate = 25
reproductionProbability = 0.1
undesirability = -1

sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax)
sugar_max = np.ones([L,L])*globalSugarMax
sugarArena_t = deepcopy(sugarArena_0)
# positions_0, visions, metabolisms, sugarlevels_0 = initializePrey(A, L, v_min, v_max, m_min, m_max, s_min, s_max)

population = Population(A, visionRange, metabolismRange, sugarLevelRange, sugarArena_t, undesirability)
# positions_t = deepcopy(positions_0)
# sugarlevels_t = deepcopy(sugarlevels_0)

#plt.pcolor(np.flip(sugarArena_0, 0))
#plt.show()
t = 0
while True:
    t += 1
    A = len(population.prey)
    A_list.append(A)

    image = getImage(population.positions, sugarArena_t, A, globalSugarMax)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title(f'Time: {t}. Agents: {A}')
    time.sleep(imageDelay)
    tk.update()
    population.updatePositions(sugarArena_t, undesirability)

    sugarArena_t = updateSugarArena(L, population.positions, sugarArena_t, growthRate, sproutRate, sugar_max)

Tk.mainloop(canvas)

# plt.plot(A_list)
# plt.show()