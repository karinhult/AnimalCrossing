import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
from copy import deepcopy
import time

def updateSugarArena(N, positions, sugarArena, g, sugar_max):
    sugarArena_updated = deepcopy(sugarArena)
    for i in range(N):
        for j in range(N):
            if [i, j] in positions.tolist():
                sugarArena_updated[i, j] = 0.0
            elif sugarArena_updated[i,j] < sugar_max[i, j]:
                sugarArena_updated[i, j] += g
    return sugarArena_updated

def updateSugarLevels(positions, sugarlevels, metabolisms, velocities, sugarArena):
    sugarLevels_updated = np.copy(sugarlevels)
    sugarInCell = np.reshape(sugarArena[(positions[:,0], positions[:,1])], (-1, 1))
    sugarLevels_updated += sugarInCell - metabolisms
    survivors = np.where(sugarLevels_updated > 0)[0]
    return positions[survivors,:], velocities[survivors], metabolisms[survivors], sugarLevels_updated[survivors]

def updatePositions(A, N, positions, velocities, sugarArena):
    positions_updated = deepcopy(positions)
    for a in range(A):
        sugarList = []
        notSugarList = []
        for i in range(-int(velocities[a]), int(velocities[a]) + 1):
            ipos = positions[a, 0] + i
            jpos = positions[a, 1]
            if [ipos, jpos] not in positions_updated.tolist() and ipos >= 0 and ipos < N:
                if sugarArena[ipos, jpos] > 0:
                    sugarList.append(np.array([i, 0]))
                else:
                    notSugarList.append(np.array([i, 0]))

        for j in range(-int(velocities[a]), int(velocities[a]) + 1):
            ipos = positions[a, 0]
            jpos = positions[a, 1] + j
            if [ipos, jpos] not in positions_updated.tolist() and jpos >= 0 and jpos < N:
                if sugarArena[ipos, jpos] > 0:
                    sugarList.append(np.array([0, j]))
                else:
                    notSugarList.append(np.array([0, j]))


        if sugarList != []:
            n = len(sugarList)
            positions_updated[a,:] += sugarList[np.random.randint(0, int(n))]
        elif notSugarList != []:
            n = len(notSugarList)
            positions_updated[a,:] += notSugarList[np.random.randint(0, int(n))]
    return positions_updated

def initializeSugarArena(N, plantProb, globalSugarMax):
    sugarArena = np.random.randint(1,globalSugarMax, size=(N,N)) * (np.random.rand(N,N) < plantProb)
    return sugarArena

#Adds road
def addRoad(pos, width, sugarArena, undesirability):
    j1 = int(pos-width/2)
    j2 = int(pos+width/2)
    sugarArena[:,j1:j2] = undesirability
    return sugarArena

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

def initializePrey(A, N, v_min, v_max, m_min, m_max, s_min, s_max):
    positions = np.random.randint(0, N, (A, 2))
    visions = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)
    
    #preys = [Prey(visions[i], metabolisms[i], sugarlevels[i], positions[i]) for i in range(A)]
    #can return prey and positions? if we want that
    return positions, velocities, metabolisms, sugarlevels

def getImage(positions, sugarArena, A):
    image = 255 - sugarArena * 40
    for a in range(A):
        image[int(positions[a,0]), int(positions[a,1])] = 0
    return np.transpose(image)

res = 500  # Animation resolution
tk = Tk()
tk.geometry(str(int(res * 1.1)) + 'x' + str(int(res * 1.3)))
tk.configure(background='white')

canvas = Canvas(tk, bd=2)  # Generate animation window
tk.attributes('-topmost', 0)
canvas.place(x=res / 20, y=res / 20, height=res, width=res)
ccolor = ['#0008FF', '#DB0000', '#12F200']

#rest = Button(tk, text='Restart', command=restart)
#rest.place(relx=0.05, rely=.85, relheight=0.12, relwidth=0.15)

plantProb = 0.5
N = 50
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
sugarArena_0 = initializeSugarArena(N, plantProb, globalSugarMax)
sugar_max = deepcopy(sugarArena_0)
sugarArena_t = deepcopy(sugarArena_0)
positions_0, velocities, metabolisms, sugarlevels_0 = initializePopulation(A, N, v_min, v_max, m_min, m_max, s_min, s_max)
positions_t = deepcopy(positions_0)
sugarlevels_t = deepcopy(sugarlevels_0)

#plt.pcolor(np.flip(sugarArena_0, 0))
#plt.show()
for t in range(500):
    positions_t = updatePositions(A, N, positions_t, velocities, sugarArena_t)
    positions_t, velocities, metabolisms, sugarlevels_t = updateSugarLevels(positions_t, sugarlevels_t, metabolisms, velocities, sugarArena_t)
    A = len(sugarlevels_t)
    A_list[t+1] = A

    image = getImage(positions_t, sugarArena_t, A)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image)).resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title('time' + str(t))
    time.sleep(1/100)
    tk.update()

    sugarArena_t = updateSugarArena(N, positions_t, sugarArena_t, g, sugar_max)

Tk.mainloop(canvas)


plt.plot(range(0,501), A_list)
plt.show()
'''
A = 3
sugarlevels = np.array([1, 2, 3])
metabolisms = np.array([2, 1, 1])
positions = np.array([[1, 1], [5, 6], [4, 3]])
velocities = np.array([2, 3, 3])
sugarArena = np.zeros((7, 7))
#sugarArena[1, 1] = 1
sugarArena[5, 6] = 3
sugarlevels, positions, metabolisms, velocities = updateSugarLevels(A, positions, sugarlevels, metabolisms, velocities, sugarArena)
print(str(positions))
print(str(velocities))
print(str(metabolisms))
print(str(sugarlevels))

positions = np.array([[1, 1], [5, 6], [4, 3]])
velocities = np.array([2, 3, 3])
sugarArena = np.zeros((7, 7))
sugarArena[1, 3] = 1
A = 3
print(str(updatePositions(A, 7, positions, velocities, sugarArena)))
'''
