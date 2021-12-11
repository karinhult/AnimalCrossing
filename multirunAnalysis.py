import sys
import subprocess
import numpy as np

from numpy.core.numeric import cross

#procs = []
args = [sys.executable, 'DataAnalysis.py', 0, 0, '16', 'roadAndCrossings']

def fileName(mode, crossingType='', n=''):
    if mode == 'noroad':
        return 'noRoad'
    if mode == 'road':
        return 'road'
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

def tabLabel(mode, crossingType='', n=''):
    if mode == 'noroad':
        return 'Without road'
    if mode == 'road':
        return 'Without crossings'
    if mode == 'amount':
        if n==1:
            return f'{n} {crossingType}'
        else:
            return f'{n} {crossingType}s'
    if mode == 'amount2':
        if n == 1:
            return f'{n} 2x {crossingType}'
        else:
            return f'{n} 2x {crossingType}s'
    elif mode == 'width':
        if n==1:
            return f'1 {n}x {crossingType}'
        else:
            return f'1 {n}x {crossingType}s'
    elif mode == 'width2':
        if n == 1:
            return f'2 {n}x {crossingType}'
        else:
            return f'2 {n}x {crossingType}s'
    elif mode == 'multi':
        if n==1:
            return f'{n} tunnel/bridge'
        else:
            return f'{n} tunnels/bridges'

def plotTitle(mode, crossingType='', n=''):
    if mode == 'noroad':
        return 'Without road'
    if mode == 'road':
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

precisions = (0, 2, 3, 3, 0)

mode = 'noCrossings'
crossingType = ''
with open(f'100runResults/Tables/{mode}.txt', 'w') as file:
    mode = 'noroad'
    args[2] = fileName(mode)
    args[3] = plotTitle(mode)
    args[4] = '16'
    args[5] = 'noRoad'
    # print(args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    data = str(proc)[3:-4].split(', ')
    data.insert(0, 0)

    data = [f'{float(data[j]):.{precisions[j]}f}' for j in range(len(data) - 1)]
    data[0] = tabLabel(mode)

    file.write(' & '.join(data) + ' \\\\\n')

    #procs.append(proc)
    #for proci in procs:
    #    proci.wait()

    mode = 'road'
    args[2] = fileName(mode)
    args[3] = plotTitle(mode)
    args[4] = '16'
    args[5] = 'road'

    # print(args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    data = str(proc)[3:-4].split(', ')
    data.insert(0, 0)

    data = [f'{float(data[j]):.{precisions[j]}f}' for j in range(len(data)-1)]
    data[0] = tabLabel(mode)

    file.write(' & '.join(data) + ' \\\\\n')

    #procs.append(proc)
    #for proci in procs:
    #    proci.wait()

args[5] = 'roadAndCrossings'
nList = (1, 2, 3, 5, 10)

for mode in ('amount', 'amount2', 'width', 'width2'):
    for crossingType in ('bridge', 'tunnel'):
        with open(f'100runResults/Tables/{mode}_{crossingType}.txt', 'w') as file:
            for i, n in enumerate(nList):
                args[2] = fileName(mode, crossingType, n)
                args[3] = plotTitle(mode, crossingType, n)

                if (mode == 'width2' and n == 10) or (mode == 'amount2' and n == 10):
                    args[4] = '17'
                else:
                    args[4] = '16'

                # print(args)
                proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

                data = str(proc)[3:-4].split(', ')
                data.insert(0, 0)

                data = [f'{float(data[j]):.{precisions[j]}f}' for j in range(len(data) - 1)]
                data[0] = tabLabel(mode, crossingType, n)

                file.write(' & '.join(data) + ' \\\\\n')
                # output[i, 1:] = np.array(str(proc)[3:-4].split(', '), dtype=float)
                # procs.append(proc)
                # for proci in procs:
                #    proci.wait()
            # np.savetxt(f'100runResults/{fileName(mode, crossingType)}.csv', output)


args[4] = '16'
nList = (1, 2, 3, 5, 10)
mode = 'multi'
output = np.zeros((5, 5))
output[:,0] = nList
with open(f'100runResults/Tables/{mode}.txt', 'w') as file:
    for i, n in enumerate(nList):
        args[2] = fileName(mode, n=n)
        args[3] = plotTitle(mode, n=n)

        proc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

        data = str(proc)[3:-4].split(', ')
        data.insert(0, 0)

        data = [f'{float(data[j]):.{precisions[j]}f}' for j in range(len(data) - 1)]
        data[0] = tabLabel(mode, n=n)

        file.write(' & '.join(data) + ' \\\\\n')

        # procs.append(proc)
        # for proci in procs:
        #    proci.wait()
