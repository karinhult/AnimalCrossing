import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
import time
import random as rnd
import itertools
from Population import *

def updateSugarArena(N, positions, sugarArena, growthRate, sproutRate, sugar_max, roadValue, roadWidth=4, hasRoad=True):
    sugarArena_updated = np.copy(sugarArena)
    nNewSugarPoints = np.random.poisson(sproutRate)
    newSugarPositions = np.random.randint(0, N, size=[nNewSugarPoints, 2])

    sugarArena_updated[newSugarPositions[:,0], newSugarPositions[:,1]] += growthRate

    sugarArena_updated = np.minimum(sugarArena_updated, sugar_max)

    sugarArena_updated[positions[:,0], positions[:,1]] = 0
    if hasRoad:
        sugarArena_updated = addRoad(N/2, roadWidth, sugarArena_updated, roadValue)
    return sugarArena_updated

def updateSugarLevels(positions, sugarlevels, metabolisms, visions, sugarArena):
    sugarLevels_updated = np.copy(sugarlevels)
    sugarInCell = (sugarArena[positions[:,0], positions[:,1]])[:,np.newaxis]
    sugarLevels_updated += sugarInCell - metabolisms
    survivors = np.where(sugarLevels_updated > 0)[0]
    return positions[survivors,:], visions[survivors], metabolisms[survivors], sugarLevels_updated[survivors]

def initializeSugarArena(L, plantProb, globalSugarMax, roadWidth=4, roadValue=-2, hasRoad=True):
    # For later: Add different sugar maximums in different parts of the arena?
    sugarArena = np.random.randint(1,globalSugarMax, size=(L,L)) * (np.random.rand(L,L) < plantProb)
    if hasRoad:
        sugarArena = addRoad(L/2, roadWidth, sugarArena, roadValue)
    return sugarArena

#Adds road
def addRoad(pos, width, sugarArena, undesirability):
    j1 = int(pos-width/2)
    j2 = int(pos+width/2)
    sugarArena[:, j1:j2] = undesirability
    return sugarArena

def initializePrey(A, N, v_min, v_max, m_min, m_max, s_min, s_max, roadWidth=4, oneSide=True):
    positions = np.random.randint(0, [N, int(N/2-roadWidth)], (A, 2))
    visions = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)

    #preys = [Prey(visions[i], metabolisms[i], sugarlevels[i], positions[i]) for i in range(A)]
    #can return prey and positions? if we want that
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
roadWidth = 4
roadValue = -2
undesirability = -2
hasRoad = True
oneSide = True

sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax, roadWidth, roadValue, hasRoad=hasRoad)
sugar_max = np.ones([L,L])*globalSugarMax
sugarArena_t = np.copy(sugarArena_0)
# positions_0, visions, metabolisms, sugarlevels_0 = initializePrey(A, L, v_min, v_max, m_min, m_max, s_min, s_max)

population = Population(A, visionRange, metabolismRange, sugarLevelRange, sugarArena_t, undesirability, oneSide=oneSide)
# positions_t = np.copy(positions_0)
# sugarlevels_t = np.copy(sugarlevels_0)

#plt.pcolor(np.flip(sugarArena_0, 0))
#plt.show()
t = 0
dead_list = []
while True:
    t += 1
    A = len(population.prey)
    A_list.append(A)
    tot_dead = sum(dead_list)

    image = getImage(population.positions, sugarArena_t, A, globalSugarMax)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title(f'Time: {t}. Agents: {A}. Dead: {tot_dead}')
    time.sleep(imageDelay)
    tk.update()
    # population.updatePositions(sugarArena_t, undesirability)
    population.updatePositions(sugarArena_t, hasRoad=hasRoad)
    dead = A - len(population.prey)
    dead_list.append(dead)
    
    population.reproduce(L, visionRange, metabolismRange, sugarLevelRange, reproductionProbability)

    sugarArena_t = updateSugarArena(L, population.positions, sugarArena_t, growthRate, sproutRate, sugar_max, undesirability, hasRoad = hasRoad)

Tk.mainloop(canvas)

# plt.plot(A_list)
# plt.show()

#'''