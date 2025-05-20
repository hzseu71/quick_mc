import os
from crip.io import imreadRaw, imwriteRaw
import numpy as np
from run_mgfpj_v3 import *
import cv2


dtype1 = np.float32
num_slices = 720
column_lists = []
l1 = imreadRaw("./sgm_bone/sgm_pmma_514_8_20mm_u_2.raw", 300, 300, nSlice=1)
l2 = imreadRaw("./sgm_bone/fe_1mm_514_8_n.raw", 300, 300, nSlice=1)

with open('./Spectrum_110kVp1.txt', 'r') as file:
    # 读取文件的每一行
    for line in file:
        # 去除每行末尾的换行符，并将字符串按某种分隔符（如空格或逗号）分割成列表
        # 这里数据是用空格分隔的
        data_for_column = line.strip().split()

        # 如果是第一行，则初始化column_lists中的每个列表
        if not column_lists:
            column_lists = [[float(item)] for item in data_for_column]
        else:
            # 对于后续的行，将每个元素添加到对应的列表中
            for i, item in enumerate(data_for_column):
                number_float = float(item)
                # print(number_float)
                column_lists[i].append(number_float)

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

new_x = np.arange(20000, 101000, 1000)
# df4 = pd.read_excel('spec.xlsx')
spec_e = np.array(column_lists[0]) # Energy	能量通道中心值
spec_w = np.array(column_lists[1]) # Weight 	该能量通道的相对光子丰度

f = interp1d(spec_e, spec_w, kind='linear')
new_y = f(new_x)
# print(x04)
spec_e = new_x / 1000
spec_w = new_y

print(spec_e)
print(spec_w)

# print(column_lists)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from crip.io import imwriteRaw, imreadRaw

df1 = pd.read_excel('../attenuation coefficient/pmma_u.xlsx')
x01 = df1['Energy(kev)'].values
y01 = df1['u'].values
x1 = np.log(x01)
y1 = np.log(y01)
xi = [i for i in range(20, 101)]
xi = np.log(xi)
yi = np.interp(xi, x1, y1)
xi = np.exp(xi)
yi = np.exp(yi)

df2 = pd.read_excel('../attenuation coefficient/fe_u.xlsx')
x02 = df2['Energy(kev)'].values
y02 = df2['u'].values
x2 = np.log(x02)
y2 = np.log(y02)
# xi表示能量范围，故复用
xi = [i for i in range(20, 101)]
xi = np.log(xi)
yi2 = np.interp(xi, x2, y2)
xi = np.exp(xi)
yi2 = np.exp(yi2)


lower = 0
higher = 0
for i in range(0, 81):
    lower += spec_w[i] * spec_e[i]
for i in range(0, 81):
    higher += spec_w[i] * spec_e[i] * np.exp(-1 * yi[i] * l1 * 0.1 * 1.19 - 1 * yi2[i] * l2 * 0.1 * 7.87)


primary = higher / lower

postlog = -np.log(primary + 1e-6)   # 加小常数防 log(0)

# imwriteRaw(primary, "./primary_514_8.raw", dtype=dtype1)

imwriteRaw(postlog, "./primary_514_9_postlog.raw", dtype=dtype1)





