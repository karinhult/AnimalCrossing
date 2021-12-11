import sys
import subprocess

from numpy.core.numeric import cross

procs = []
args = [sys.executable, 'DataAnalysis.py', 0, 0, '16', 'roadAndCrossings']

def fileName(mode, crossingType, n):
    if mode == 'noroad':
        return 'noRoad'
    if mode == 'nocross':
        return 'noCrossings'
    if mode == 'amount':
        return f'{n}{crossingType}s'
    if mode == 'amount2':
        return f'{n}{crossingType}s2wide'
    elif mode == 'width':
        return f'1x{n}wide{crossingType}s'
    elif mode == 'width2':
        return f'2x{n}wide{crossingType}s'
    elif mode == 'multi':
        return f'{n}tunnels{n}bridges'

def plotTitle(mode, crossingType, n):
    if mode == 'noroad':
        return 'Without road'
    if mode == 'nocross':
        return 'With road and no crossings'
    if mode == 'amount':
        return f'With road and {n} {crossingType}{"s" if n >= 2 else ""}'
    if mode == 'amount2':
        return f'With road and {n} {crossingType}{"s" if n >= 2 else ""}, 2 wide'
    elif mode == 'width':
        return f'With road and one {n} wide {crossingType}'
    elif mode == 'width2':
        return f'With road and two {n} wide {crossingType}s'
    elif mode == 'multi':
        return f'With road and {n} tunnels and {n} bridges'

mode = 'noroad'
args[2] = fileName(mode, '', 0)
args[3] = plotTitle(mode, '', 0)
args[4] = '16'
args[5] = 'noRoad'
proc = subprocess.Popen(args)
procs.append(proc)
for proc in procs:
    proc.wait()

mode = 'nocross'
args[2] = fileName(mode, '', 0)
args[3] = plotTitle(mode, '', 0)
args[4] = '16'
args[5] = 'road'
proc = subprocess.Popen(args)
procs.append(proc)
for proc in procs:
    proc.wait()

args[5] = 'roadAndCrossings'
for mode in ('amount', 'amount2', 'width', 'width2'):
    for crossingType in ('bridge', 'tunnel'):
        for n in (1, 2, 3, 5, 10):
            args[2] = fileName(mode, crossingType, n)
            args[3] = plotTitle(mode, crossingType, n)

            if (mode == 'width2' and n == 10) or (mode == 'amount2' and n == 10):
                args[4] = '17'
            else:
                args[4] = '16'

            # print(args)

            proc = subprocess.Popen(args)
            procs.append(proc)

            for proc in procs:
                proc.wait()

args[4] = '16'

mode = 'multi'
for n in (1, 2, 3, 5, 10):
    args[2] = fileName(mode, crossingType, n)
    args[3] = plotTitle(mode, crossingType, n)

    # print(args)

    proc = subprocess.Popen(args)
    procs.append(proc)

    for proc in procs:
        proc.wait()