import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
from scipy.signal import savgol_filter

def getData(runs, initialFileName, skip=16):
    A = np.zeros((runs, 2001))
    for i in range(runs):
        filename = initialFileName + 'run' + str(int(i + 1))
        A[i, :] = np.genfromtxt(filename + '.csv', delimiter=',', skip_header=skip)
    return A

def getSteadyStateMean(A):
    return np.mean(A)

def getStandardDeviationSteadyStateMean(A):
    A_mean = np.mean(A[:,1200:], axis=1)
    return np.sqrt(np.var(A_mean))

def getMeanStandardDeviationSteadyState(A):
    A_var = np.var(A[:,1200:], axis=1)
    return np.mean(np.sqrt(A_var))

def getMeanAndStandardDeviations(A):
    meanA = getSteadyStateMean(A)
    stdMeanA = getStandardDeviationSteadyStateMean(A)
    meanStdA = getMeanStandardDeviationSteadyState(A)
    return meanA, stdMeanA, meanStdA

def plotRandomA(A, runs, saveRandom, directoryname, plotfilename, title, delay):
    iBlue = np.random.randint(0,runs)
    fig1, ax = plt.subplots(1, 1, figsize=(5, 4))
    ax.plot(A[1, :], color='silver', label='All simulations')
    for i in range(1, runs):
        ax.plot(A[i,:], color = 'silver')
    ax.plot(A[iBlue, :], color='tab:blue', label='Random simulation')
    ax.plot(np.mean(A, axis=0), color='tab:orange', label='$\mu_A$')
    # ax.plot(savgol_filter(np.mean(A, axis=0), 201, 3), color='green')
    if delay < 2001:
        ax.plot([delay, delay], [-100, 300], color='black', linestyle = 'dashed', label='Mean delay')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of agents')
    ax.set_title(title)
    ax.set_ylim([0,170])
    if saveRandom:
        fig1.savefig(directoryname + '/Figures/pdf/standard/' + plotfilename + '.pdf')
        fig1.savefig(directoryname + '/Figures/png/standard/' + plotfilename + '.png')
        plt.close(fig1)
    else:
        plt.show()

    fig2, ax = plt.subplots(1, 1, figsize=(5, 4))
    ax.plot(A[1, :], color='silver', label='All simulations')
    for i in range(1, runs):
        ax.plot(A[i, :], color='silver')
    ax.plot(A[iBlue, :], color='tab:blue', label='Random simulation')
    # ax.plot(savgol_filter(np.mean(A, axis=0), 201, 3), color='green')
    if delay < 2001:
        ax.plot([delay, delay], [-100, 300], color='black', linestyle='dashed', label='Mean delay')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of agents')
    ax.set_title(title)
    ax.set_ylim([0, 170])
    if saveRandom:
        fig2.savefig(directoryname + '/Figures/pdf/random/' + plotfilename + '.pdf')
        fig2.savefig(directoryname + '/Figures/png/random/' + plotfilename + '.png')
        plt.close(fig2)
    else:
        plt.show()

    fig3, ax = plt.subplots(1, 1, figsize=(5, 4))
    ax.plot(np.mean(A, axis=0), color='tab:blue', label='$\mu_A$')
    ax.plot(np.mean(A, axis=0) + np.sqrt(np.var(A, axis=0)), color='silver', label='$\mu_A\pm\\sigma_A$')
    ax.plot(np.mean(A, axis=0) - np.sqrt(np.var(A, axis=0)), color='silver')
    # ax.plot(savgol_filter(np.mean(A, axis=0), 201, 3), color='green')
    if delay < 2001:
        ax.plot([delay, delay], [-100, 300], color='black', linestyle='dashed', label='Mean delay')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of agents')
    ax.set_title(title)
    ax.set_ylim([0, 170])
    if saveRandom:
        fig3.savefig(directoryname + '/Figures/pdf/mean/' + plotfilename + '.pdf')
        fig3.savefig(directoryname + '/Figures/png/mean/' + plotfilename + '.png')
        plt.close(fig3)
    else:
        plt.show()


def getSteadyStateDelay(A):
    varMax = .5
    interval = 200

    meanRun = np.mean(A, axis=0)
    for i, window in enumerate(np.lib.stride_tricks.sliding_window_view(meanRun, interval)):
        if np.var(window) < varMax:
            return i

    return np.nan # Only occurs if no value is found

def getInflectionPoint(A):
    derivativeTolerance = 1e-4
    windowMeanTolerance = 3
    subsequentMeanTolerance = 5
    meanRun = np.mean(A, axis=0)
    peakIndex = np.argmax(meanRun)
    smoothedMeanRun = savgol_filter(meanRun, 201, 3)
    windowMeanSize = 100
    windowMean = np.full(len(smoothedMeanRun), np.inf)
    windowMean[:-windowMeanSize+1] = np.mean(np.lib.stride_tricks.sliding_window_view(smoothedMeanRun, windowMeanSize), axis=1)
    subsequentMean = (np.cumsum(smoothedMeanRun[::-1]) / np.arange(1, len(smoothedMeanRun)+1))[::-1]
    secondOrderDer = np.gradient(np.gradient(smoothedMeanRun))
    inflectionPoints = np.where((np.abs(secondOrderDer) < derivativeTolerance) & (np.abs(smoothedMeanRun - windowMean) < windowMeanTolerance) & \
        (np.abs(smoothedMeanRun - subsequentMean) < subsequentMeanTolerance))[0]
    inflectionPoints = inflectionPoints[inflectionPoints > peakIndex + 100]

    return inflectionPoints[0]

def getNoRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = ''):
    directoryName = 'Results/' + 'noRoadAndNoBridge/'
    initialFileName = directoryName + 'noRoad_'
    A = getData(runs, initialFileName)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A)
    '''
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
    '''
    delay = getInflectionPoint(A)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, directoryname, plotfilename, title, delay)
    return meanA, stdMeanA, meanStdA, delay

def getRoadData(runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = '', directoryName='noRoadAndNoBridge', topDirectory='Results'):
    initialFileName = f'{topDirectory}/{directoryName}/' + 'road_'
    A = getData(runs, initialFileName)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A)
    # meanDelay, stdDelay = getSteadyStateDelay(A)
    # delay = getSteadyStateDelay(A)
    delay = getInflectionPoint(A)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, directoryname, plotfilename, title, delay)
    return meanA, stdMeanA, meanStdA, delay

def getAnimalCrossingAnalysis(filename, directoryName, runs = 20, plotRandom = False, saveRandom = False, plotfilename = '', title = '', skip=16, topDirectory='Results'):
    initialFileName = f'{topDirectory}/{directoryName}/{filename}_'
    A = getData(runs, initialFileName, skip=skip)
    meanA, stdMeanA, meanStdA = getMeanAndStandardDeviations(A)
    # meanDelay, stdDelay = getSteadyStateDelay(A)
    # delay = getSteadyStateDelay(A)
    delay = getInflectionPoint(A)
    if plotRandom:
        plotRandomA(A, runs, saveRandom, topDirectory, plotfilename, title, delay)
    return meanA, stdMeanA, meanStdA, delay

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12

if len(sys.argv) >= 2:
    print(f'\n{sys.argv[2]}:')
    print(str(getAnimalCrossingAnalysis(sys.argv[4], sys.argv[1], runs = 100, plotRandom = True, title=sys.argv[2], saveRandom=True, plotfilename=f'{sys.argv[1]}', skip=int(sys.argv[3]), topDirectory='100runResults')))

# print(str(getAnimalCrossingAnalysis('1x2widetunnels', plotRandom = True, title='Temp', saveRandom=True, plotfilename='100runResults/1x2widetunnels', topDirectory='100runResults')))

# TODO
# - Get directory
# - For loop that reads data from file and gets mean values of stuff, etc
# - Plots

#print(str(getNoRoadData(plotRandom = True, title='Without road', saveRandom=True, plotfilename='Results/WithoutRoad')))
#print(str(getRoadData(plotRandom = True, title='With road, without crossings', saveRandom=True, plotfilename='Results/WithRoad')))

#print('\n One tunnel:')
# print(str(getAnimalCrossingAnalysis('1tunnel', plotRandom = True, title='With road and one tunnel', saveRandom=True, plotfilename='Results/WithRoadAnd01Tunnels')))

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

#print('\n 1x1 Bridge:')
#print(str(getAnimalCrossingAnalysis('1x1wideBridge', plotRandom = True, title='With road and one 1 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x1wideBridge')))

#print('\n 1x2 Bridge:')
#print(str(getAnimalCrossingAnalysis('1x2wideBridge', plotRandom = True, title='With road and one 2 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x2wideBridge')))

#print('\n 1x3 Bridge:')
#print(str(getAnimalCrossingAnalysis('1x3wideBridge', plotRandom = True, title='With road and one 3 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x4wideBridge')))

#print('\n 1x5 Bridge:')
#print(str(getAnimalCrossingAnalysis('1x5wideBridge', plotRandom = True, title='With road and one 5 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x5wideBridge')))

#print('\n 1x10 Bridge:')
#print(str(getAnimalCrossingAnalysis('1x10wideBridge', plotRandom = True, title='With road and one 10 times wide bridge', saveRandom=True, plotfilename='Results/WithRoadAnd1x10wideBridge')))

#print('\n 2x1 Bridges:')
#print(str(getAnimalCrossingAnalysis('2x1wideBridges', plotRandom = True, title='With road and two 1 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x1wideBridge')))

#print('\n 2x2 Bridges:')
#print(str(getAnimalCrossingAnalysis('2x2wideBridges', plotRandom = True, title='With road and two 2 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x2wideBridge')))

#print('\n 2x3 Bridges:')
#print(str(getAnimalCrossingAnalysis('2x3wideBridges', plotRandom = True, title='With road and two 3 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x3wideBridge')))

#print('\n 2x5 Bridges:')
#print(str(getAnimalCrossingAnalysis('2x5wideBridges', plotRandom = True, title='With road and two 5 times wide bridges', saveRandom=True, plotfilename='Results/WithRoadAnd2x5wideBridge')))

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

# print('\n One bridge 2 wide:')
# print(str(getAnimalCrossingAnalysis('1bridge2wide', plotRandom = True, title='With road and one bridge', saveRandom=True, plotfilename='Results/WithRoadAnd01Bridges2wide')))

# print('\n Two bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('2bridge2wide', plotRandom = True, title='With road and two bridges', saveRandom=True, plotfilename='Results/WithRoadAnd02Bridges2wide')))

# print('\n Three bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('3bridge2wide', plotRandom = True, title='With road and three bridges', saveRandom=True, plotfilename='Results/WithRoadAnd03Bridges2wide')))

# print('\n Five bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('5bridge2wide', plotRandom = True, title='With road and five bridges', saveRandom=True, plotfilename='Results/WithRoadAnd05Bridges2wide')))

# print('\n Ten bridges 2 wide:')
# print(str(getAnimalCrossingAnalysis('10bridge2wide', skip=17, plotRandom = True, title='With road and ten bridges', saveRandom=True, plotfilename='Results/WithRoadAnd10Bridges2wide')))
