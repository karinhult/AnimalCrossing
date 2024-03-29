import numpy as np
import matplotlib.pyplot as plt
import csv

def getData(runs, initialFileName, skip=16):
    A = np.zeros((runs, 2001))
    for i in range(runs):
        filename = initialFileName + 'run' + str(int(i + 1))
        A[i, :] = np.genfromtxt(filename + '.csv', delimiter=',', skip_header=skip)
    return A

def getSteadyStateMean(A):
    return np.mean(A)

def getVarianceSteadyStateMean(A, runs):
    A_mean = np.mean(A[:,1001:], axis=1)
    return np.var(A_mean)

def getMeanStandardDeviationSteadyState(A, runs):
    A_var = np.var(A[:,1001:], axis=1)
    return np.mean(np.sqrt(A_var))

def getMeanAndStandardDeviations(A, runs):
    meanA = getSteadyStateMean(A)
    stdMeanA = np.sqrt(getVarianceSteadyStateMean(A, runs))
    meanStdA = getMeanStandardDeviationSteadyState(A, runs)
    return meanA, stdMeanA, meanStdA

def plotRandomA(A, runs, saveRandom, plotfilename, title, delay):
    iBlue = np.random.randint(0,runs)
    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    for i in range(runs):
        ax.plot(A[i,:], color = 'silver')
    ax.plot(A[iBlue, :], color='blue')
    ax.plot(np.mean(A, axis=0), color='red')
    if delay < 2001:
        ax.plot([delay, delay], [-100, 300], color='black', linestyle = 'dashed', label='Mean delay')
        ax.legend(loc='upper right')
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of agents')
    ax.set_title(title)
    ax.set_ylim([0,170])
    if saveRandom:
        fig.savefig(plotfilename + '.pdf')
    else:
        plt.show()

def getSteadyStateDelay(A, runs):
    varMax = 2
    interval = 200

    meanRun = np.mean(A, axis=0)
    for i, window in enumerate(np.lib.stride_tricks.sliding_window_view(meanRun, interval)):
        if np.var(window) < varMax:
            return i

    return np.nan # Only occurs if no value is found

def getNoRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    directoryName = 'Results/' + 'noRoadAndNoBridge/'
    initialFileName = directoryName + 'noRoad_'
    A = getData(runs, initialFileName)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A, runs)
    delay = np.zeros(runs)
    intervall = 200
    fraction = 0.9
    for j in range(runs):
        steadyStateDelay = np.inf
        for i in range(2001 - intervall + 1):
            meanA_intervall = np.mean(A[j, i:i + intervall])
            if meanA_intervall > fraction * meanA:
                steadyStateDelay = i+intervall/2
                break
        delay[j] = steadyStateDelay
    meanDelay = np.mean(delay)
    stdDelay = np.sqrt(np.var(delay))
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title, meanDelay)
    return meanA, stdMeanA, meanStdA, meanDelay, stdDelay

def getRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    directoryName = 'Results/' + 'noRoadAndNoBridge/'
    initialFileName = directoryName + 'road_'
    A = getData(runs, initialFileName)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A, runs)
    # meanDelay, stdDelay = getSteadyStateDelay(A, runs)
    delay = getSteadyStateDelay(A, runs)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title, delay)
    return meanA, stdMeanA, meanStdA, delay

def getAnimalCrossingAnalysis(directoryName, runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = '', skip=16):
    initialFileName = 'Results/' + directoryName + '/roadAndCrossings_'
    A = getData(runs, initialFileName, skip=skip)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A, runs)
    # meanDelay, stdDelay = getSteadyStateDelay(A, runs)
    delay = getSteadyStateDelay(A, runs)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, plotfilename, title, delay)
    return meanA, stdMeanA, meanStdA, delay

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
# TODO
# - Get directory
# - For loop that reads data from file and gets mean values of stuff, etc
# - Plots

#print(str(getNoRoadData(plotRandom = True, title='Without road', saveRandom=True, plotfilename='Results/WithoutRoad')))
#print(str(getRoadData(plotRandom = True, title='With road, without crossings', saveRandom=True, plotfilename='Results/WithRoad')))

#print('\n One tunnel:')
#print(str(getAnimalCrossingAnalysis('1tunnel', plotRandom = True, title='With road and one tunnel', saveRandom=True, plotfilename='Results/WithRoadAnd01Tunnels')))

#print('\n Two tunnels:')
#print(str(getAnimalCrossingAnalysis('2tunnel', plotRandom = True, title='With road and two tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd02Tunnels')))

#print('\n Three tunnels:')
#print(str(getAnimalCrossingAnalysis('3tunnel', plotRandom = True, title='With road and three tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd03Tunnels')))

#print('\n Five tunnels:')
#print(str(getAnimalCrossingAnalysis('5tunnel', plotRandom = True, title='With road and five tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd05Tunnels')))

#print('\n Ten tunnels:')
#print(str(getAnimalCrossingAnalysis('10tunnel', plotRandom = True, title='With road and ten tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd10Tunnels')))

#print('\n One bridge:')
#print(str(getAnimalCrossingAnalysis('1bridge', plotRandom = True, title='With road and one bridge', saveRandom=True, plotfilename='Results/WithRoadAnd01Bridges')))

#print('\n Two bridges:')
#print(str(getAnimalCrossingAnalysis('2bridge', plotRandom = True, title='With road and two bridges', saveRandom=True, plotfilename='Results/WithRoadAnd02Bridges')))

#print('\n Three bridges:')
#print(str(getAnimalCrossingAnalysis('3bridge', plotRandom = True, title='With road and three bridges', saveRandom=True, plotfilename='Results/WithRoadAnd03Bridges')))

#print('\n Five bridges:')
#print(str(getAnimalCrossingAnalysis('5bridge', plotRandom = True, title='With road and five bridges', saveRandom=True, plotfilename='Results/WithRoadAnd05Bridges')))

#print('\n Ten bridges:')
#print(str(getAnimalCrossingAnalysis('10bridge', plotRandom = True, title='With road and ten bridges', saveRandom=True, plotfilename='Results/WithRoadAnd10Bridges')))

print('\n 1x1 Bridge:')
print(str(getAnimalCrossingAnalysis('1x1wideBridge', plotRandom = True, title='With road and one 1 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x1wideBridge')))

print('\n 1x2 Bridge:')
print(str(getAnimalCrossingAnalysis('1x2wideBridge', plotRandom = True, title='With road and one 2 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x2wideBridge')))

print('\n 1x3 Bridge:')
print(str(getAnimalCrossingAnalysis('1x3wideBridge', plotRandom = True, title='With road and one 3 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x4wideBridge')))

print('\n 1x5 Bridge:')
print(str(getAnimalCrossingAnalysis('1x5wideBridge', plotRandom = True, title='With road and one 5 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x5wideBridge')))

print('\n 1x10 Bridge:')
print(str(getAnimalCrossingAnalysis('1x10wideBridge', plotRandom = True, title='With road and one 10 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x10wideBridge')))

print('\n 2x1 Bridges:')
print(str(getAnimalCrossingAnalysis('2x1wideBridges', plotRandom = True, title='With road and two 1 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x1wideBridge')))

print('\n 2x2 Bridges:')
print(str(getAnimalCrossingAnalysis('2x2wideBridges', plotRandom = True, title='With road and two 2 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x2wideBridge')))

print('\n 2x3 Bridges:')
print(str(getAnimalCrossingAnalysis('2x3wideBridges', plotRandom = True, title='With road and two 3 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x3wideBridge')))

print('\n 2x5 Bridges:')
print(str(getAnimalCrossingAnalysis('2x5wideBridges', plotRandom = True, title='With road and two 5 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x5wideBridge')))

#print('\n 2x10 Bridges:')
#print(str(getAnimalCrossingAnalysis('2x10wideBridges', plotRandom = True, title='With road and two 10 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x10wideBridge', skip=17)))



# print('\n One tunnel 2 wide:')
# print(str(getAnimalCrossingAnalysis('1tunnel2wide', plotRandom = True, title='With road and one tunnel', saveRandom=True, plotfilename='Results/WithRoadAnd01Tunnels2wide')))

# print('\n Two tunnels 2 wide:')
# print(str(getAnimalCrossingAnalysis('2tunnel2wide', plotRandom = True, title='With road and two tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd02Tunnels2wide')))

# print('\n Three tunnels 2 wide:')
# print(str(getAnimalCrossingAnalysis('3tunnel2wide', plotRandom = True, title='With road and three tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd03Tunnels2wide')))

# print('\n Five tunnels 2 wide:')
# print(str(getAnimalCrossingAnalysis('5tunnel2wide', plotRandom = True, title='With road and five tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd05Tunnels2wide')))

# print('\n Ten tunnels 2 wide:')
# print(str(getAnimalCrossingAnalysis('10tunnel2wide', skip=17, plotRandom = True, title='With road and ten tunnels', saveRandom=True, plotfilename='Results/WithRoadAnd10Tunnels2wide')))

print('\n One bridge 2 wide:')
print(str(getAnimalCrossingAnalysis('1bridge2wide', plotRandom = True, title='With road and one bridge', saveRandom=True, plotfilename='Results/WithRoadAnd01Bridges2wide')))

# print('\n Two bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('2bridge2wide', plotRandom = True, title='With road and two bridges', saveRandom=True, plotfilename='Results/WithRoadAnd02Bridges2wide')))

# print('\n Three bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('3bridge2wide', plotRandom = True, title='With road and three bridges', saveRandom=True, plotfilename='Results/WithRoadAnd03Bridges2wide')))

# print('\n Five bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('5bridge2wide', plotRandom = True, title='With road and five bridges', saveRandom=True, plotfilename='Results/WithRoadAnd05Bridges2wide')))

print('\n Ten bridges 2 wide:')
print(str(getAnimalCrossingAnalysis('10bridge2wide', skip=17, plotRandom = True, title='With road and ten bridges', saveRandom=True, plotfilename='Results/WithRoadAnd10Bridges2wide')))
