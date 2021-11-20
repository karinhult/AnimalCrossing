import numpy as np
import matplotlib.pyplot as plt
import random as rnd

def updatePositions(A, L, positions, velocities, sugarArena):
    positions_updated = np.copy(positions)

    globalSugarList_x = np.where(sugarArena != 0)[0].reshape((-1,1))
    globalSugarList_y = np.where(sugarArena != 0)[1].reshape((-1,1))
    globalSugarList = np.concatenate((globalSugarList_x, globalSugarList_y), 1)
    for a in range(A):
        distance = np.linalg.norm(positions[a,:] - globalSugarList[:,:], axis=1)
        iSugarList = np.where(distance <= velocities[a])[0]
        nSugarPossibilities = iSugarList.shape[0]
        if nSugarPossibilities > 0:
            positions_updated[a,:] = globalSugarList[rnd.choice(iSugarList),:]
        else:
            outsideArena = True
            while outsideArena:
                v = np.random.uniform(0, velocities[a])
                theta = np.random.uniform(0, 2*np.pi)
                velocity = np.array([np.rint(v*np.cos(theta)), np.rint(v*np.sin(theta))])
                newPosition = positions_updated[a,:] + velocity
                if newPosition[0] >= 0 and newPosition[0] < L and newPosition[1] >= 0 and newPosition[1] < L and np.linalg.norm(velocity, axis=0) <= velocities[a]:
                    positions_updated[a, :] = newPosition
                    outsideArena = False
    return positions_updated
