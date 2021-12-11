import sys
import subprocess
import numpy as np

from numpy.core.numeric import cross

args = [sys.executable, 'DataAnalysis.py', 0, 0, '16']

def fileName(mode, crossingType, n=''):
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

nList = (1, 2, 3, 5, 10)

precisions = (0, 2, 3, 3, 0)

for mode in ('amount', 'width', 'width2'):
    for crossingType in ('bridge', 'tunnel'):
        with open(f'100runResults/{fileName(mode, crossingType)}.txt', 'w') as file:
            for i, n in enumerate(nList):
                args[2] = fileName(mode, crossingType, n)
                args[3] = plotTitle(mode, crossingType, n)

                if mode == 'width2' and n == 10:
                    args[4] = '17'
                else:
                    args[4] = '16'

                # print(args)

                proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

                data = str(proc)[3:-4].split(', ')
                data.insert(0, n)

                data = [f'{float(data[i]):.{precisions[i]}f}' for i in range(len(data))]

                file.write(' & '.join(data) + ' \\\\\n')
                # output[i, 1:] = np.array(str(proc)[3:-4].split(', '), dtype=float)
            # np.savetxt(f'100runResults/{fileName(mode, crossingType)}.csv', output)




args[4] = '16'

mode = 'multi'
output = np.zeros((5, 5))
output[:,0] = nList
with open(f'100runResults/{fileName(mode, crossingType)}.txt', 'w') as file:
    for i, n in enumerate(nList):
        args[2] = fileName(mode, crossingType, n)
        args[3] = plotTitle(mode, crossingType, n)

        proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

        data = str(proc)[3:-4].split(', ')
        data.insert(0, n)

        data = [f'{float(data[i]):.{precisions[i]}f}' for i in range(len(data))]

        file.write(' & '.join(data) + ' \\\\\n')