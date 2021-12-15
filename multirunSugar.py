import sys
import subprocess

from numpy.core.numeric import cross

procs = []
args = [sys.executable, 'SugarscapeEx.py', 0, 0, 0, 0]

def fileName(mode, crossingType, n):
    if crossingType == 3:
        crossingType = 'bridges'
    elif crossingType == 4:
        crossingType = 'tunnels'

    if mode == 'amount':
        return f'{n}{crossingType}'
    elif mode == 'width':
        return f'1x{n}wide{crossingType}'
    elif mode == 'width2':
        return f'2x{n}wide{crossingType}'
    elif mode == 'multi':
        return f'{n}tunnels{n}bridges'

for mode in ('amount', 'width', 'width2'):
    args[2] = mode
    for crossingType in (3, 4):
        args[3] = '0'
        args[4] = '0'
        for n in ('1', '2', '3', '5', '10'):
            args[crossingType] = n
            args[5] = fileName(mode, crossingType, n)

            proc = subprocess.Popen(args)
            procs.append(proc)

    for proc in procs:
        proc.wait()

mode = 'multi'
args[2] = mode
for n in ('1', '2', '3', '5', '10'):
    args[3] = n
    args[4] = n
    args[5] = fileName(mode, crossingType, n)

    print(args)

    proc = subprocess.Popen(args)
    procs.append(proc)

for proc in procs:
    proc.wait()