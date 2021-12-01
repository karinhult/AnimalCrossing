import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
import time
import random as rnd
import itertools
import csv
from Population import *

def updateSugarArena(L, positions, sugarArena, growthRate, sproutRate, sugar_max, roadValue, roadWidth=4, hasRoad=True,
                     tunnelIndices = np.array([]), bridgeIndices = np.array([]), tunnelValue = -1):
    sugarArena_updated = np.copy(sugarArena)
    nNewSugarPoints = np.random.poisson(sproutRate)
    newSugarPositions = np.random.randint(0, L, size=[nNewSugarPoints, 2])

    sugarArena_updated[newSugarPositions[:,0], newSugarPositions[:,1]] += growthRate

    sugarArena_updated = np.minimum(sugarArena_updated, sugar_max)

    sugarArena_updated[positions[:,0], positions[:,1]] = 0
    if hasRoad:
        sugarArena_updated = addRoad(L, roadWidth, sugarArena_updated, roadValue, tunnelIndices, bridgeIndices, tunnelValue)
    return sugarArena_updated

def updateSugarLevels(positions, sugarlevels, metabolisms, visions, sugarArena):
    sugarLevels_updated = np.copy(sugarlevels)
    sugarInCell = (sugarArena[positions[:,0], positions[:,1]])[:,np.newaxis]
    sugarLevels_updated += sugarInCell - metabolisms
    survivors = np.where(sugarLevels_updated > 0)[0]
    return positions[survivors,:], visions[survivors], metabolisms[survivors], sugarLevels_updated[survivors]

def initializeSugarArena(L, plantProb, globalSugarMax, roadWidth=4, roadValue=-2, hasRoad=True,
                         tunnelIndices = np.array([]), bridgeIndices = np.array([]), tunnelValue = -1):
    # For later: Add different sugar maximums in different parts of the arena?
    sugarArena = np.random.randint(1,globalSugarMax, size=(L,L)) * (np.random.rand(L,L) < plantProb)
    if hasRoad:
        sugarArena = addRoad(L, roadWidth, sugarArena, roadValue, tunnelIndices, bridgeIndices, tunnelValue)
    return sugarArena

#Adds road
def addRoad(L, width, sugarArena, roadValue, tunnelIndices, bridgeIndices, tunnelValue):
    j1 = int((L-width)/2)
    j2 = int((L+width)/2)

    roadIndices = np.arange(L)

    if len(bridgeIndices) > 0:
        noBridgeIndices = [index for index in roadIndices if index not in bridgeIndices]
    else:
        noBridgeIndices = roadIndices

    sugarArena[noBridgeIndices, j1:j2] = roadValue

    if len(tunnelIndices) > 0:
        sugarArena[tunnelIndices, j1:j2] = tunnelValue

    return sugarArena

def initializePrey(A, N, v_min, v_max, m_min, m_max, s_min, s_max, roadWidth=4, oneSide=True):
    positions = np.random.randint(0, [N, int(N/2-roadWidth)], (A, 2))
    visions = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)

    #preys = [Prey(visions[i], metabolisms[i], sugarlevels[i], positions[i]) for i in range(A)]
    #can return prey and positions? if we want that
    return positions, visions, metabolisms, sugarlevels

def getImage(positions, sugarArena, A, globalSugarMax, roadValue, tunnelValue):
    width = np.shape(sugarArena)[0]
    image = np.zeros((width, width, 3))
    image[:,:,0] = 175 # Red soil
    image[sugarArena > 0, :] = 0
    image[:,:,1] = (sugarArena *(1-1.5*255)/globalSugarMax).astype(int) # Green food
    image[sugarArena == tunnelValue, :] = 150
    image[sugarArena == roadValue, :] = 75
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
L = 100
A = 25
A_list = [A]
globalSugarMax = 4
visionRange = (3, 8)
metabolismRange = (1, 3)
sugarLevelRange = (5, 25)
growthRate = 2
sproutRate = 10
reproductionProbability = 0.01
maxSugar = 20
roadWidth = 4
roadValue = -2
tunnelValue = -1
hasRoad = False
oneSide = False
saveDataToFile = True

hasCrossings = False
if hasCrossings and hasRoad:
    iRoadMin = int((L - roadWidth) / 2)
    iRoadMax = int((L + roadWidth) / 2 - 1)
    bridgeIndices = np.array([L/4]).astype(int)
    tunnelIndices = np.array([3*L/4]).astype(int)
    crossingMin = np.zeros((len(tunnelIndices) + len(bridgeIndices), 2))
    crossingMax = np.zeros((len(tunnelIndices) + len(bridgeIndices), 2))
    for i in range(len(tunnelIndices)):
        crossingMin[i,:] = np.array([tunnelIndices[i], iRoadMin])
        crossingMax[i,:] = np.array([tunnelIndices[i], iRoadMax])
    for i in range(len(bridgeIndices)):
        crossingMin[i+len(tunnelIndices), :] = np.array([bridgeIndices[i], iRoadMin])
        crossingMax[i+len(tunnelIndices), :] = np.array([bridgeIndices[i], iRoadMax])
    sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax, roadWidth, roadValue, hasRoad=hasRoad,
                         tunnelIndices = tunnelIndices, bridgeIndices = bridgeIndices, tunnelValue = tunnelValue)
else:
    sugarArena_0 = initializeSugarArena(L, plantProb, globalSugarMax, roadWidth, roadValue, hasRoad=hasRoad)
sugar_max = np.ones([L,L])*globalSugarMax
sugarArena_t = np.copy(sugarArena_0)

population = Population(A, visionRange, metabolismRange, sugarLevelRange, sugarArena_t, roadValue, roadWidth, oneSide=oneSide)
# positions_t = np.copy(positions_0)
# sugarlevels_t = np.copy(sugarlevels_0)

t = 0
dead_list = []
born_list = []
born = 0
tot_dead = sum(dead_list)
while t<100:
    t += 1

    image = getImage(population.positions, sugarArena_t, A, globalSugarMax, roadValue, tunnelValue)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image),'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title(f'Time: {t}. Agents: {A}. Dead: {tot_dead}. Last born: {born}')
    time.sleep(imageDelay)
    tk.update()

    # population.updatePositions(sugarArena_t, roadValue)
    if hasCrossings:
        population.updatePositions(sugarArena_t, hasRoad=hasRoad, crossingMin = crossingMin, crossingMax = crossingMax, maxSugar = maxSugar)
    else:
        population.updatePositions(sugarArena_t, hasRoad=hasRoad, maxSugar = maxSugar)
    population.removeDeadAnimals()
    Anew = len(population.prey)
    dead = A - Anew
    dead_list.append(dead)

    population.reproduce(L, visionRange, metabolismRange, sugarLevelRange, reproductionProbability, hasRoad, roadWidth)
    born = len(population.prey) - Anew
    born_list.append(born)

    if hasCrossings:
         sugarArena_t = updateSugarArena(L, population.positions, sugarArena_t, growthRate, sproutRate, sugar_max, roadValue, hasRoad = hasRoad,
                     tunnelIndices = tunnelIndices, bridgeIndices = bridgeIndices, tunnelValue = tunnelValue)
    else:
        sugarArena_t = updateSugarArena(L, population.positions, sugarArena_t, growthRate, sproutRate, sugar_max, roadValue, hasRoad = hasRoad)

    A = len(population.prey)
    A_list.append(A)
    tot_dead = sum(dead_list)
tk.destroy()
Tk.mainloop(canvas)

print(str(A))
# NOTE: Not finished and has NOT been tested yet!!
if saveDataToFile:
    settings = [f"plantProb = {plantProb}", f"L = {L}", f"globalSugarMax = {globalSugarMax}", f"visionRange = {visionRange}",
                f"metabolismRange = {metabolismRange}", f"sugarLevelRange = {sugarLevelRange}", f"growthRate = {growthRate}",
                f"sproutRate = {sproutRate}", f"reproductionProbability = {reproductionProbability}", f"roadWidth = {roadWidth}",
                f"hasRoad = {hasRoad}", f"oneSide = {oneSide}", f"hasCrossings = {hasCrossings}"]

    data = np.array([A_list, dead_list, born_list]).T

    dataHeader = "A_list: \n"
    fileName = input("Name of data file: ")
    outputFile = open(fileName, "w")
    for item in settings:
        outputFile.write(item + "\n")
    outputFile.write(dataHeader)
    dataWriter = csv.writer(outputFile)
    dataWriter.writerow(A_list)
    #put writing functions here

    outputFile.close()
    print("\nResult saved in ", fileName)



# plt.plot(A_list)
# plt.show()

#'''
