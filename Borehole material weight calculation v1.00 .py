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

start_point = [295000, 2765000] #TWD97 [X, Y]
grid_size = [1000, 1000, 1] #meter [X, Y, Z]
grid_number = [3, 3, 0] #number[X, Y, Z]


target_grid = []
grid = {}

def plot():
    plt.plot(location['source_x'], location['source_y'], 'bo')


def mix(borehole_data):

    def slect(ID, length):
        if ID == 1 :
            return np.array([length, 0.0, 0.0, 0.0])
        elif ID == 2 :
            return np.array([0.0, length, 0.0, 0.0])
        elif ID == 3 :
            return np.array([0.0, 0.0, length, 0.0])
        elif ID == 4 :
            return np.array([0.0, 0.0, 0.0, length])
        else:
            print('偵測到無效的材料ID, 程序即將崩潰')
            return None


    def clip(S, E, borehole_data):
        i = borehole_data
        out_info = np.array([0.0, 0.0, 0.0, 0.0])
        
        if E > i[-1][1]:
            E = i[-1][1]
    
        for j in range(0, len(i)):
            if i[j][1] > S:
                order_S = j
                break
        
        for j in range(0, len(i)):
            if i[j][0] < E <= i[j][1]:
                order_E = j
                break
    
        if order_S == order_E:
            out_info += slect(i[j][2], E-S)
            
        if order_S != order_E:
            for j in range(order_S, order_E+1):
                
                if j == order_S:
                    out_info += slect(i[j][2], i[j][1] - S)
                    continue
                elif j == order_E:
                    out_info += slect(i[j][2], E- i[j][0])
                    continue
                else:
                    out_info += slect(i[j][2], i[j][1] - i[j][0])
                    continue
        return out_info
    

    out_len_cal_list = []
    for i in range(len(borehole_data)):
        out_len_cal_list.append(borehole_data[i][-1][1])
    out_len = math.ceil(max(out_len_cal_list))
    
    out_array = [[0.0, 0.0, 0.0, 0.0]]
    for i in range(0, out_len-1):
        out_array.append([0.0, 0.0, 0.0, 0.0])
    out_array = np.array(out_array)


    for i in borehole_data:
        S = 0
        E = 1
        for j in range(0, math.ceil(i[-1][1])):
            out_array[j] += clip(S, E, i)
            S += 1
            E += 1
    
    mixed_material = []
    for i in out_array:
        H = max(i)
        judge = []
        m_info = 0
        for j in range(0, 4):
            if i[j] == H:
                judge.append(j+1) #此處開始以材料代碼表示
        
        if len(judge) == 1:
            m_info  = judge[0]
        
        elif len(judge) > 1:
            if 3 in judge :
                m_info = 3
            elif 2 in judge:
                m_info = 2
            elif 1 in judge:
                m_info = 1
            elif 4 in judge:
                m_info = 4
        
        elif len(judge) <= 0:
            print('一米單元計算錯誤，請檢查資料')
        
        mixed_material.append(m_info)
    return mixed_material




'''
#檢索資料
'''
print('檢索資料', end = '')
counter_remind = 10

start_X = start_point[0]
end_X = start_point[0] + grid_size[0]
start_Y = start_point[1]
end_Y = start_point[1] + grid_size[1]
for i in range(grid_number[1]):
    
    if (i/grid_number[1])*100 >= counter_remind :
        counter_remind += 10
        print('.', end = '')
    
    
    for j in range(grid_number[0]):
        elevation = []
        usingborehole = []
        for k in range(len(location)):
            if location['source_x'][k] in range(start_X, end_X + 1) and location['source_y'][k] in range(start_Y, end_Y + 1):
                elevation.append(location['elevation'][k])
                usingborehole.append(location['hole_no'][k])
                
        if len(usingborehole) > 0 :
            elevation = round(statistics.mean(elevation), 3)
            target_grid.append('%s-%s'%(j, i))
            grid['%s-%s'%(j, i)] = {'site' : [start_X, end_X, start_Y, end_Y], 'elevation' : elevation, 'usingborehole' : usingborehole}
        
        start_X += grid_size[0]
        end_X += grid_size[0]
    start_X = start_point[0]
    end_X = start_point[0] + grid_size[0]
    start_Y += grid_size[1]
    end_Y += grid_size[1]

print('done')


'''
#將資料寫入記憶體
'''
print('將資料寫入記憶體', end = '')
counter_remind = 10
counter_lenth = len(target_grid)
counter = 0

for i in target_grid :
    
    counter += 1
    if (counter/counter_lenth)*100 >= counter_remind:
        counter_remind += 10
        print('.', end = '')

    
    usingborehole = grid[i]['usingborehole']
    borehole_data = []
    for j in usingborehole:
        single_borehole = []
        stat = 0
        for k in range(len(df)):
            if df['hole_no'][k] == j :
                single_borehole.append([df['top_depth'][k], df['bottom_depth'][k], df['code'][k]])
                stat = 1
            elif stat == 1: #為了提升運算效率，抓到一次連續的鑽井資料後，即停止掃描，若資料有問題或怕有邏輯問題產生，請把這個elif移除
                break  #同上
        borehole_data.append(single_borehole)
    grid[i]['borehole_data'] = borehole_data

print('done')


'''
#運算
'''
print('運算', end = '')

counter_start = 10
counter = 0
counter_length = len(target_grid)
for i in target_grid:

    counter += 1
    if counter/counter_length*100 >= counter_start:
        counter_start += 10
        print('.', end = '')
    
    grid[i]['mixed_material'] = mix(grid[i]['borehole_data'])

print('done')



    
    








