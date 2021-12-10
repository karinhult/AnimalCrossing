import sys
import subprocess

from numpy.core.numeric import cross

procs = []
args = [sys.executable, 'DataAnalysis.py', 0, 0, '16']

def fileName(mode, crossingType, n):
    if mode == 'amount':
        return f'{n}{crossingType}s'
    elif mode == 'width':
        return f'1x{n}wide{crossingType}s'
    elif mode == 'width2':
        return f'2x{n}wide{crossingType}s'
    elif mode == 'multi':
        return f'{n}tunnels{n}bridges'

def plotTitle(mode, crossingType, n):
    if mode == 'amount':
        return f'With road and {n} {crossingType}{"s" if n >= 2 else ""}'
    elif mode == 'width':
        return f'With road and one {n} wide {crossingType}'
    elif mode == 'width2':
        return f'With road and two {n} wide {crossingType}s'
    elif mode == 'multi':
        return f'With road and {n} tunnels and {n} bridges'

for mode in ('amount', 'width', 'width2'):
    for crossingType in ('bridge', 'tunnel'):
        for n in (1, 2, 3, 5, 10):
            args[2] = fileName(mode, crossingType, n)
            args[3] = plotTitle(mode, crossingType, n)

            if mode == 'width2' and n == 10:
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