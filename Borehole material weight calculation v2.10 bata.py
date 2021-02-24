'''
其實我不是很會寫code Q Q
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics
import math
import time
import csv

time_start = time.time()

location = pd.read_excel("location.xlsx")
df = pd.read_excel("code.xlsx")

'''
初始設定
'''
start_point = [280000, 2750000] #TWD97 [X, Y]
grid_size = [100, 100, 1] #meter [X, Y, Z] at least 3 X 3 X 1
grid_number = [500, 500, 0] #number[X, Y, Z]


'''
輸入所需副程式
'''
def plot(): #把點畫出來，方便決定起始點與網格大小、數量
    plt.plot(location['source_x'], location['source_y'], 'bo')
    
    
def order_find(X, Y): #給定鑽井位置並回傳所在網格，以及該網格中心座標。若鑽井位於格線上將會判定為兩個網隔皆包含該鑽井。

    if X == start_point[0] and Y == start_point[1]: #為避免ZeroDivisionError而將這個事件獨立出來，不過其實不獨立出來好像沒關係。
        return [['1-1', int(start_point[0] + (0.5 * grid_size[0])), int(start_point[1] + (0.5 * grid_size[1]))]]
    
    X_order = []
    if X == start_point[0]: #左邊界
        X_order.append(1)
    elif  X ==  (grid_size[0] * grid_number[0]) + start_point[0]: #右邊界
        X_order.append(grid_number[0])
    elif X in range(start_point[0] + grid_size[0], (grid_size[0] * grid_number[0]) + start_point[0], grid_size[0]): #垂直格線
        X_order.append(int((X - start_point[0]) / grid_size[0]))
        X_order.append(int(X_order[0] + 1))
    else:
        X_order.append(math.ceil((X - start_point[0]) / grid_size[0])) #其它
    
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
    for i in X_order: #有了兩個方向的序列後，即可給定網格位置。
        for j in Y_order:
            out.append(['%s-%s' %(i, j), int(start_point[0] + ((i-0.5)*grid_size[0])), int(start_point[1] + ((j-0.5)*grid_size[1]))]) #網格過小就不建議使用int了，不過這邊就方便使然
    
    return out
        

def mix(borehole_data): #輸入一組或以上鑽井資料並輸出權重計算成果
    def slect(ID, length): #輸出材料對應的矩陣
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

    def clip(S, E, borehole_data): #輸入一筆鑽井資料並給定任意深度範圍，給出該深度範圍中的材料厚度，將給出一個一維四項的矩陣。
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
    for i in range(len(borehole_data)): #找出最深的鑽井深度
        out_len_cal_list.append(borehole_data[i][-1][1])
    out_len = math.ceil(max(out_len_cal_list))
    
    out_array = [[0.0, 0.0, 0.0, 0.0]]
    for i in range(0, out_len-1): #建立垂向空白網格，若垂直網格大小需要改變(!=1)，這邊應該需要改。
        out_array.append([0.0, 0.0, 0.0, 0.0])
    out_array = np.array(out_array)


    for i in borehole_data: #將每一筆鑽井資料中的每一分段填入空白網格。若垂直網格大小需要改變(!=1)，S跟E應該需要改。
        S = 0
        E = 1
        for j in range(0, math.ceil(i[-1][1])):
            out_array[j] += clip(S, E, i)
            S += 1
            E += 1
    
    mixed_material = []
    for i in out_array: #計算輸出網格的材料權重
        H = max(i) #找出佔比最高的材料代碼
        judge = []
        m_info = 0
        for j in range(0, 4):
            if i[j] == H: #找出佔比最高的代碼位置，注意，有可能會有一個或以上的最高值，這種情況需要進一步判斷。
                judge.append(j+1) #此處開始以材料代碼表示
        
        if len(judge) == 1: #如果佔比最高的材料只有一種，該網格指定為該材料。
            m_info  = judge[0]
        
        elif len(judge) > 1: #如果佔比最高的材料有兩種以上，將以給定的順序歸類，順序為 3> 2 > 1 > 4
            if 3 in judge :
                m_info = 3
            elif 2 in judge:
                m_info = 2
            elif 1 in judge:
                m_info = 1
            elif 4 in judge:
                m_info = 4
        
        elif len(judge) <= 0: #代碼非1~4就會跳這個錯誤
            print('一米單元計算錯誤，請檢查資料')
        
        mixed_material.append(m_info) #決定該網格的材料後，寫入網格資訊
    return mixed_material


def mix_out(grid, target_grid):
    Out_list = [['id', 'name', 'x', 'y', 'z', 'material']]
    ID = 1
    
    for i in target_grid:
        name = i
        x = grid[i]['grid_center'][0]
        y = grid[i]['grid_center'][1]
        elevation = grid[i]['grid_elevation']
        
        for material in grid[i]['mixed_material']:
            Out_list.append([ID, name, x, y, round(elevation, 5), material])
            elevation -= grid_size[2]
        Out_list.append([ID, name, x, y, round(elevation, 5), material])
        
        ID += 1
    
    with open('mix_out.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(Out_list)
    
    print('mix_out done')
    
    return



'''
開始計算
'''
T = 0
grid = {}
target_grid = []



'''
計算每筆位置資訊所在網格，並寫入各井的高程、網格中心
'''
for i in range(0, len(location)):
    if math.ceil(location['source_x'][i]) in range(start_point[0], (grid_size[0] * grid_number[0]) + start_point[0]) and math.ceil(location['source_y'][i]) in range(start_point[1], (grid_size[1] * grid_number[1]) + start_point[1]):
        order = order_find(location['source_x'][i], location['source_y'][i])
        for j in order:
            if j[0] not in target_grid:
                target_grid.append(j[0])
                grid[j[0]] = {'usingborehole' : [], 'grid_center' : [ j[1], j[2] ], 'grid_elevation' : [], 'borehole_data' : []}
                
            grid[j[0]]['usingborehole'].append(location['hole_no'][i])
            grid[j[0]]['grid_elevation'].append(location['elevation'][i])
    
        T += 1



'''
將材料資訊建立dic，加速後續運算。
'''
code_dic = {}
for i in range(0, len(df)):
    if df['top_depth'][i] == 0 :
        if df['hole_no'][i] not in code_dic:
            code_dic[df['hole_no'][i]] = []
        else:
            print('Error : repeat name in ', df['hole_no'][i])
            continue
        
    try:
        code_dic[df['hole_no'][i]].append([df['top_depth'][i], df['bottom_depth'][i], df['code'][i]])
        
    except KeyError:
        print('KeyError in ', df['hole_no'][i])
        continue
    
    except:
        print('unexcept error in line ', i+2)
        continue


'''
將材料資訊寫入網格，並計算網格高程。
'''
for i in target_grid:
    for j in grid[i]['usingborehole']:

        try:
            grid[i]['borehole_data'].append(code_dic[j])
            
        except KeyError:
            print('KeyError in grid %s, borehole %s not find.' %(i, j))
            continue
        
        except:
            print('unexcept error in grid %s - %s ' %(i, j))
            continue

    grid[i]['grid_elevation'] = round(statistics.mean(grid[i]['grid_elevation']), 5)


'''
計算並寫入各網格之鑽井資料混合成果
'''
for i in target_grid:  
    grid[i]['mixed_material'] = mix(grid[i]['borehole_data'])



mix_out(grid, target_grid)

time_end = time.time()
time_c= time_end - time_start
print('time cost', time_c, 's')
print('count %s times'%T)











