'''
其實我不是很會寫code Q Q
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics
import math

location = pd.read_excel("location.xlsx")
df = pd.read_excel("code.xlsx")

start_point = [280000, 2750000] #TWD97 [X, Y]
grid_size = [100, 100, 1] #meter [X, Y, Z] at least 3 X 3 X 1
grid_number = [500, 500, 0] #number[X, Y, Z]


target_grid = []
grid = {}

def plot():
    plt.plot(location['source_x'], location['source_y'], 'bo')
    
    
def order_find(X, Y):

    if X == start_point[0] and Y == start_point[1]:
        return ['1-1']
    
    X_order = []
    if X == start_point[0]:
        X_order.append(1)
    elif  X ==  (grid_size[0] * grid_number[0]) + start_point[0]:
        X_order.append(grid_number[0])
    elif X in range(start_point[0] + grid_size[0], (grid_size[0] * grid_number[0]) + start_point[0], grid_size[0]):
        X_order.append(int((X - start_point[0]) / grid_size[0]))
        X_order.append(int(X_order[0] + 1))
    else:
        X_order.append(math.ceil((X - start_point[0]) / grid_size[0]))
    
    Y_order = []
    if Y == start_point[1]:
        Y_order.append(1)
    elif Y == (grid_size[1] * grid_number[1]) + start_point[1]:
        Y_order.append(grid_number[1])
    elif Y in range(start_point[1] + grid_size[1], (grid_size[1] * grid_number[1]) + start_point[1], grid_size[1]):
        Y_order.append(int((Y - start_point[1]) / grid_size[1]))
        Y_order.append(int(Y_order[0] + 1))
    else:
        Y_order.append(math.ceil((Y - start_point[1]) / grid_size[1]))
    
    out = []
    for i in X_order:
        for j in Y_order:
            out.append('%s-%s' %(i, j))
    
    return out
        





import time
time_start = time.time()
T = 0
target_grid = []
for i in range(0, len(location)):
    if math.ceil(location['source_x'][i]) in range(start_point[0], (grid_size[0] * grid_number[0]) + start_point[0]) and math.ceil(location['source_y'][i]) in range(start_point[1], (grid_size[1] * grid_number[1]) + start_point[1]):
        order = order_find(location['source_x'][i], location['source_y'][i])
        for j in order:
            if j not in target_grid:
                target_grid.append(j)
                grid[j] = {'usingborehole' : []}
                
            grid[j]['usingborehole'].append(location['hole_no'][i])
    
    T += 1
        
        
time_end = time.time()
time_c= time_end - time_start
print('time cost', time_c, 's')
print('count %s times'%T)


O = []
OD = {}
for i in target_grid:
    L = len(grid[i]['usingborehole'])
    if L not in O:
        O.append(L)
        OD[L] = 0
    OD[L] += 1
        









