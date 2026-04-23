#!/usr/bin/python
''' 
author: Hynek Reznicek (reznicek@cs.cas.cz)
Program for finding possible procesor topology (on simple domain run) 
'''
import itertools
import argparse

#=================================
parser = argparse.ArgumentParser()
parser.add_argument('-nx', type=int, help='nx, number of cells in x')
parser.add_argument('-ny', type=int, help='ny, number of cells in y')
#parser.add_argument('--opt', dest='opt', default=True, action='store_true') #type=bool,
parser.add_argument('--no_opt', dest='opt', action='store_false', help='switch off the optimization - cells/core NOT divisible by 4')
parser.set_defaults(opt=True)
parser.add_argument('-T', type=int, help='cpus per node')
args = parser.parse_args()
#================================

nx = args.nx
ny = args.ny
opt = args.opt 
node_cpus = args.T

def npe(n):
    npea = []
    if (n % 4 != 0): raise ValueError('number of cells has to be divisible by 4 !! (due to Multigrid psolver)')
    else:
        for i in reversed(range(4,int(n/4)+1,1)):
            if n % i == 0:            #if i divides n
                div = int(n / i)      #divisor needs to be divisible by 2 nad > 10 
                if ((div % 2 == 0)  and (div>9)): npea.append([i, int(n / i)])
    return(npea)

npex = npe(nx)
npey = npe(ny)
# print('possible npex =', [np[0] for np in npex], '\n', 'cells/core =', [np[1] for np in npex])
#Cartesian product
product = list(itertools.product(npex, npey))
##domain per core should be 1:1 (or worst 1:2)   AND the number of cores has to be even (for Ariel)
product = [x for x in product if (((x[0][1]/x[1][1]) > 0.499) and ((x[0][1]/x[1][1]) < 2.001))]
product = [x for x in product if (x[0][0]*x[1][0] % 2 == 0)]
# print(product)    # print(product[1][0][0])
print('nx =', nx, ', ny =', ny, ', opt =', opt, ', node_cpus (-T) =', node_cpus)
print('+++', 'possible topology',  '+++\n', \
'(N/core divisible by 2', ', domain/core is a square (1:1, at worst 1:2), the multiplication of cores is even)')
if opt:
    ##best possibility divisors  (divisible by 4 - best for multigrid)
    product = [x for x in product if ((x[0][1] % 4 == 0) and (x[1][1] % 4 == 0))]
    print('---','best topology', '(N/core divisible by 4 <=> opt = True):')
if (len(product) == 0): print(' NONE (try to switch off optimization)')
for element in product:
    print('npex = ', element[0][0], 'npey = ', element[1][0], '(', element[0][0]*element[1][0], ')',  \
    '  domain/core Nx*Ny = ', element[0][1],'x', element[1][1], \
    ' nodes = ', round(element[0][0]*element[1][0] / node_cpus, 2) )