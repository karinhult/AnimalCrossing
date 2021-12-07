import numpy as np
import matplotlib.pyplot as plt
import csv

def getData(runs, initialFileName):
    A = np.zeros((runs, 2001))
    for i in range(runs):
        filename = initialFileName + 'run' + str(int(i + 1))
        A[i, :] = np.genfromtxt(filename + '.csv', delimiter=',', skip_header=16)
    return A

def getSteadyStateMean(A):
    return np.mean(A)

def getVarianceSteadyStateMean(A, runs):
    A_mean = np.zeros(runs)
    for i in range(runs):
        A_mean[i] = np.mean(A[i, 1001:])
    return np.var(A_mean)

def getMeanVarianceSteadyState(A, runs):
    A_var = np.zeros(runs)
    for i in range(runs):
        A_var[i] = np.var(A[i,1001:])
    return np.mean(A_var)

def getMeanAndVariances(A, runs):
    meanA = getSteadyStateMean(A)
    varMeanA = getVarianceSteadyStateMean(A, runs)
    meanVarA = getMeanVarianceSteadyState(A, runs)
    return meanA, varMeanA, meanVarA

def plotRandomA(A, runs, saveRandom, plotfilename, title):
    iBlue = np.random.randint(0,runs)
    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    for i in range(runs):
        ax.plot(range(0,2001), A[i,:], color = 'silver')
    ax.plot(range(0, 2001), A[iBlue, :], color='blue')
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of agents $A$')
    ax.set_title(title)
    if saveRandom:
        fig.savefig(plotfilename + '.pdf')
    else:
        plt.show()

def getSteadyStateDelay(A, runs):
    meanSteadyStateA = getNoRoadData()[0]
    meanDelay = 0
    intervall = 100
    fraction = 0.9
    for j in range(runs):
        steadyStateDelay = np.inf
        for i in range(2001-intervall+1):
            meanA = np.mean(A[j,i:i+intervall])
            if meanA > fraction*meanSteadyStateA:
                steadyStateDelay = i
                break
        meanDelay += steadyStateDelay/runs
    return meanDelay

def getNoRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    directoryName = 'Results/' + '2021-12-07_16.16.37/'
    initialFileName = directoryName + 'noRoad_'
    A = getData(runs, initialFileName)
    meanA, varMeanA, meanVarA = getMeanAndVariances(A, runs)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title)
    meanDelay = 0
    intervall = 100
    fraction = 0.9
    for j in range(runs):
        steadyStateDelay = np.inf
        for i in range(2001 - intervall + 1):
            meanA_intervall = np.mean(A[j, i:i + intervall])
            if meanA_intervall > fraction * meanA:
                steadyStateDelay = i
                break
        meanDelay += steadyStateDelay / runs
    return meanA, varMeanA, meanVarA, meanDelay

def getRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    directoryName = 'Results/' + '2021-12-07_16.16.37/'
    initialFileName = directoryName + 'road_'
    A = getData(runs, initialFileName)
    meanA, varMeanA, meanVarA = getMeanAndVariances(A, runs)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title)
    meanDelay = getSteadyStateDelay(A, runs)
    return meanA, varMeanA, meanVarA, meanDelay

def getAnimalCrossingAnalysis(directoryName, runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    initialFileName = 'Results/' + directoryName + '/roadAndCrossings_'
    A = getData(runs, initialFileName)
    meanA, varMeanA, meanVarA = getMeanAndVariances(A, runs)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title)
    meanDelay = getSteadyStateDelay(A, runs)
    return meanA, varMeanA, meanVarA, meanDelay

# TODO
# - Get directory
# - For loop that reads data from file and gets mean values of stuff, etc
# - Plots

print(str(getNoRoadData(plotRandom = True, title='Without road', saveRandom=True, plotfilename='Results/WithoutRoad')))
print(str(getRoadData(plotRandom = True, title='With road, without crossings', saveRandom=True, plotfilename='Results/WithRoad')))

print('\n One tunnel:')
print(str(getAnimalCrossingAnalysis('2021-12-07_16.45.11', plotRandom = True, title='With road and one tunnel', saveRandom=True, plotfilename='Results/WithRoadAnd01Tunnels')))

print('\n Two tunnels:')
print(str(getAnimalCrossingAnalysis('2021-12-07_16.45.29', plotRandom = True, title='With road and two tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd02Tunnels')))

print('\n Three tunnels:')
print(str(getAnimalCrossingAnalysis('2021-12-07_16.45.56', plotRandom = True, title='With road and three tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd03Tunnels')))

print('\n Five tunnels:')
print(str(getAnimalCrossingAnalysis('2021-12-07_16.46.21', plotRandom = True, title='With road and five tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd05Tunnels')))

print('\n Ten tunnels:')
print(str(getAnimalCrossingAnalysis('2021-12-07_16.46.47', plotRandom = True, title='With road and ten tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd10Tunnels')))

print('\n One bridge:')
print(str(getAnimalCrossingAnalysis('2021-12-07_17.23.15', plotRandom = True, title='With road and one bridge', saveRandom=True, plotfilename='Results/WithRoadAnd01Bridges')))

print('\n Two bridges:')
print(str(getAnimalCrossingAnalysis('2021-12-07_17.23.27', plotRandom = True, title='With road and two bridges', saveRandom=True, plotfilename='Results/WithRoadAnd02Bridges')))

print('\n Three bridges:')
print(str(getAnimalCrossingAnalysis('2021-12-07_17.23.42', plotRandom = True, title='With road and three bridges', saveRandom=True, plotfilename='Results/WithRoadAnd03Bridges')))

print('\n Five bridges:')
print(str(getAnimalCrossingAnalysis('2021-12-07_17.24.05', plotRandom = True, title='With road and five bridges', saveRandom=True, plotfilename='Results/WithRoadAnd05Bridges')))

print('\n Ten bridges:')
print(str(getAnimalCrossingAnalysis('2021-12-07_17.24.24', plotRandom = True, title='With road and ten bridges', saveRandom=True, plotfilename='Results/WithRoadAnd10Bridges')))