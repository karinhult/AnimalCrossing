import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image
from PIL import ImageTk as itk
from copy import deepcopy
import sys
import time
import os
np.set_printoptions(threshold=sys.maxsize)

def updateSugarArena(N, positions, sugarArena, g, sugar_max):
    sugarArena_updated = np.copy(sugarArena)
    for i in range(N):
        for j in range(N):
            if [i, j] in positions.tolist():
                sugarArena_updated[i, j] = 0.0
            elif sugarArena_updated[i,j] < sugar_max[i, j]:
                sugarArena_updated[i, j] += g
    return sugarArena_updated

def updateSugarLevels(A, positions, sugarlevels, metabolisms, velocities, sugarArena):
    sugarlevels_updated = deepcopy(sugarlevels)
    deadList = []
    for a in range(A):
        sugarInCell = sugarArena[positions[a,0], positions[a,1]]
        sugarlevels_updated[a] += sugarInCell - metabolisms[a]
        if sugarlevels_updated[a] < 0:
            deadList.append(a)

    positions = np.delete(positions, deadList, 0)
    sugarlevels_updated = np.delete(sugarlevels_updated, deadList, 0)
    metabolisms = np.delete(metabolisms, deadList, 0)
    velocities = np.delete(velocities, deadList, 0)
    return positions, velocities, metabolisms, sugarlevels_updated

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

def initializeSugarArena(N, radius_inner, pos1, pos2, globalSugarMax):
    sugarArena = np.zeros((N,N))
    for i in range(N):
        for j in range(N):
            for s in range(1, globalSugarMax + 1):
                if ((pos1[0] - i)**2 + (pos1[1] - j)**2 < radius_inner * s) or ((pos2[0] - i)**2 + (pos2[1] - j)**2 < radius_inner * s):
                    sugarArena[i,j] += 1
    return sugarArena

def initializePopulation(A, N, v_min, v_max, m_min, m_max, s_min, s_max):
    positions = np.random.randint(0, N, (A, 2))
    velocities = np.random.randint(v_min, v_max+1, (A, 1))
    metabolisms = np.random.randint(m_min, m_max+1, (A, 1)).astype(float)
    sugarlevels = np.random.randint(s_min, s_max+1, (A, 1)).astype(float)
    return positions, velocities, metabolisms, sugarlevels

def getImage(positions, sugarArena, A, globalSugarMax):
    width = np.shape(sugarArena)[0]
    image = np.zeros((width, width, 3))
    image[:, :, 0] = 0  # Red soil
    #image[sugarArena > 0, :] = 0
    image[:, :, 1] = (sugarArena * 255 * 0.75 / globalSugarMax).astype(int)  # Green food
    for a in range(A):
        image[int(positions[a, 0]), int(positions[a, 1]), :] = 255  # White agents
    return image
'''
def getImage(positions, sugarArena, A, globalSugarMax, roadValue, tunnelValue):
    width = np.shape(sugarArena)[0]
    image = np.zeros((width, width, 3))
    image[:,:,0] = 0 # Red soil
    image[sugarArena > 0, :] = 0
    image[:,:,1] = (sugarArena *255 * 1.5/globalSugarMax).astype(int) # Green food
    image[sugarArena == tunnelValue, :] = 150
    image[sugarArena == roadValue, :] = 100
    for a in range(A):
        image[int(positions[a,0]), int(positions[a,1]), :] = 255 # White agents
    return image
'''
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

N = 50
A = 200
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
sugarArena_0 = initializeSugarArena(N, round(N*3/4,0), np.array([round(N/3.5,0), round(N/3.5,0)]), np.array([N-round(N/3.5,0), N-round(N/3.5,0)]), globalSugarMax)
sugar_max = np.copy(sugarArena_0)
sugarArena_t = deepcopy(sugarArena_0)
positions_0, velocities, metabolisms, sugarlevels_0 = initializePopulation(A, N, v_min, v_max, m_min, m_max, s_min, s_max)
positions_t = deepcopy(positions_0)
sugarlevels_t = deepcopy(sugarlevels_0)

#plt.pcolor(np.flip(sugarArena_0, 0))
#plt.show()
for t in range(30):
    positions_t = updatePositions(A, N, positions_t, velocities, sugarArena_t)
    positions_t, velocities, metabolisms, sugarlevels_t = updateSugarLevels(A, positions_t, sugarlevels_t, metabolisms, velocities, sugarArena_t)
    A = len(sugarlevels_t)
    A_list[t+1] = A

    image = getImage(positions_t, sugarArena_t, A, globalSugarMax)
    img = itk.PhotoImage(Image.fromarray(np.uint8(image), 'RGB').resize((res, res), resample=Image.BOX))
    canvas.create_image(0, 0, anchor=NW, image=img)
    tk.title('time' + str(t))
    time.sleep(1/20)
    if t==0 or t==24:
        filename = 'Presentation/sugarscape_t' + str(int(t)) + '.png'
        img._PhotoImage__photo.write(filename)

    tk.update()

    sugarArena_t = updateSugarArena(N, positions_t, sugarArena_t, g, sugar_max)

Tk.mainloop(canvas)


plt.plot(range(0,501), A_list)
plt.show()

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
