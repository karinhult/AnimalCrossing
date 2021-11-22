import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
from copy import deepcopy
import time
import random as rnd

def updateSugarArena(N, positions, sugarArena, g, sugar_max):
    sugarArena_updated = deepcopy(sugarArena)
    for i in range(N):
        for j in range(N):
            if [i, j] in positions.tolist():
                sugarArena_updated[i, j] = 0.0
            elif sugarArena_updated[i,j] < sugar_max[i, j]:
                sugarArena_updated[i, j] += g
    return sugarArena_updated

def updateSugarArenaPois(N, positions, sugarArena, g, growthRate, sugar_max):
    sugarArena_updated = deepcopy(sugarArena)
    nNewSugarPoints = np.random.poisson(growthRate)
    newSugarPositions = np.random.randint(0, N, size=[nNewSugarPoints, 2])

    sugarArena_updated[newSugarPositions[:,0], newSugarPositions[:,1]] += g

    #globalSugarList_x = np.where(sugarArena != 0)[0].reshape((-1, 1))
    #globalSugarList_y = np.where(sugarArena != 0)[1].reshape((-1, 1))
    #globalSugarList = np.concatenate((globalSugarList_x, globalSugarList_y), 1)

    #sugarAndAgent = np.intersect2d(positions, globalSugarList)
    #sugarArena_updated[sugarAndAgent] = 0
    sugarArena_updated[positions[:,0], positions[:,1]] = 0

    return sugarArena_updated

def updateSugarLevels(positions, sugarlevels, metabolisms, visions, sugarArena):
    sugarLevels_updated = np.copy(sugarlevels)
    sugarInCell = (sugarArena[positions[:,0], positions[:,1]])[:,np.newaxis]
    sugarLevels_updated += sugarInCell - metabolisms
    survivors = np.where(sugarLevels_updated > 0)[0]
    return positions[survivors,:], visions[survivors], metabolisms[survivors], sugarLevels_updated[survivors]

def updatePositions(A, L, positions, visions, sugarArena):
    positions_updated = np.copy(positions)

    globalSugarList_x = np.where(sugarArena != 0)[0].reshape((-1,1))
    globalSugarList_y = np.where(sugarArena != 0)[1].reshape((-1,1))
    globalSugarList = np.concatenate((globalSugarList_x, globalSugarList_y), 1)
    for a in range(A):
        distance = np.linalg.norm(positions[a,:] - globalSugarList[:,:], axis=1)
        iSugarList = np.where(distance <= visions[a])[0]
        nSugarPossibilities = iSugarList.shape[0]
        if nSugarPossibilities > 0:
            positions_updated[a,:] = globalSugarList[rnd.choice(iSugarList),:]
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
    return sugarArena

#Adds road
def addRoad(pos, width, sugarArena, undesirability):
    j1 = int(pos-width/2)
    j2 = int(pos+width/2)
    sugarArena[:,j1:j2] = undesirability
    return sugarArena

def initializePrey(A, N, v_min, v_max, m_min, m_max, s_min, s_max):
    positions = np.random.randint(0, N, (A, 2))
    visions = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)

    #preys = [Prey(visions[i], metabolisms[i], sugarlevels[i], positions[i]) for i in range(A)]
    #can return prey and positions? if we want that
    return positions, visions, metabolisms, sugarlevels

def getImage(positions, sugarArena, A, globalSugarMax):
    width = np.shape(sugarArena)[0]
    image = np.zeros((50, 50, 3))
    image[:,:,1] = 175 # Green grass
    image[sugarArena > 0, :] = 0
    image[:,:,0] = (sugarArena * 1.5*255/globalSugarMax).astype(int) # Red food
    for a in range(A):
        image[int(positions[a,0]), int(positions[a,1]), :] = 255 # White agents
    # breakpoint()
    return np.transpose(image, (1, 0, 2))

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
A = 400
A_list = np.zeros(501)
A_list[0] = A
globalSugarMax = 4
v_min = 1
v_max = 6
m_min = 1
m_max = 4
s_min = 5
s_max = 25
g = 1
growthRate = 25

sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax)
sugar_max = np.ones([L,L])*globalSugarMax
sugarArena_t = deepcopy(sugarArena_0)
positions_0, visions, metabolisms, sugarlevels_0 = initializePrey(A, L, v_min, v_max, m_min, m_max, s_min, s_max)

positions_t = deepcopy(positions_0)
sugarlevels_t = deepcopy(sugarlevels_0)

#plt.pcolor(np.flip(sugarArena_0, 0))
#plt.show()
for t in range(500):
    positions_t = updatePositions(A, L, positions_t, visions, sugarArena_t)
    positions_t, visions, metabolisms, sugarlevels_t = updateSugarLevels(positions_t, sugarlevels_t, metabolisms, visions, sugarArena_t)
    A = len(sugarlevels_t)
    A_list[t+1] = A

    image = getImage(positions_t, sugarArena_t, A, globalSugarMax)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title('time' + str(t))
    time.sleep(imageDelay)
    tk.update()

    sugarArena_t = updateSugarArenaPois(L, positions_t, sugarArena_t, g, growthRate, sugar_max)

Tk.mainloop(canvas)

# plt.plot(A_list)
# plt.show()