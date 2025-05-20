import os
import matlab.engine

# 启动 MATLAB 引擎
eng = matlab.engine.start_matlab()

from crip.io import imreadRaw,imwriteRaw
import numpy as np

# 定义三个 .raw 文件的路径
file_paths = [
    'E:/BaiduNetdiskDownload/homework/phantom/baseline_water_modified.raw',
    'E:/BaiduNetdiskDownload/homework/phantom/baseline_bone_modified.raw'
    # 'path/to/file3.raw'
]

# 定义对应的密度数组
densities = [1.0,1.920]

# 用于存储读取的 .raw 文件数据
raw_arrays = []

# 读取 .raw 文件
for file_path in file_paths:
    raw_data = imreadRaw(file_path,h=256,w=256,dtype=np.float32,nSlice=256)
    raw_arrays.append(raw_data)

# 检查是否成功读取所有文件
if len(raw_arrays) == len(file_paths):
    # 分别乘以对应的密度
    scaled_arrays = []
    for i in range(len(raw_arrays)):
        scaled_array = raw_arrays[i] * densities[i]
        scaled_arrays.append(scaled_array)

    # 取最大值
    print(np.array(scaled_arrays).shape)
    max_array = np.maximum.reduce(scaled_arrays)
    print(max_array.shape)

    # 保存结果
    output_file_path = 'E:/BaiduNetdiskDownload/homework/phantom/result1.raw'
    imwriteRaw(max_array,output_file_path)


try:
    # 主作业目录
    homework_dir = r'E:\BaiduNetdiskDownload\homework'
    # 需要添加到 MATLAB 搜索路径的文件夹
    folders_to_add = ['MCGPU-for-MATLAB-main', 'matlab_functions-main', 'mangoct-dev', 'mango_matlab-master']

    for folder in folders_to_add:
        folder_path = os.path.join(homework_dir, folder)
        if os.path.exists(folder_path):
            try:
                # 直接调用 addpath 函数，不接收返回值
                eng.addpath(folder_path)
                print(f"成功尝试添加路径: {folder_path}")

                # 如果是 matlab_functions-main 文件夹，进一步查找子文件夹
                if folder == 'matlab_functions-main':
                    for root, dirs, files in os.walk(folder_path):
                        for sub_dir in dirs:
                            sub_folder_path = os.path.join(root, sub_dir)
                            eng.addpath(sub_folder_path)
                            print(f"成功尝试添加子文件夹路径: {sub_folder_path}")
            except Exception as e:
                print(f"添加路径时出现异常: {folder_path}，异常信息: {e}")
        else:
            print(f"路径不存在: {folder_path}")

    # 查看 MATLAB 搜索路径
    # search_path = eng.path()
    # print("MATLAB 搜索路径:")
    # print(search_path)

    # 要运行的 MATLAB 脚本的完整路径
    script_path = r'E:\BaiduNetdiskDownload\homework\bone\process_mcgpu.m'
    # 运行 MATLAB 脚本
    eng.run(script_path, nargout=0)

    print("MATLAB 脚本执行完成。")

except Exception as e:
    print(f"执行 MATLAB 脚本时出现错误: {e}")

finally:
    # 关闭 MATLAB 引擎
    eng.quit()



from run_mgfpj_v3 import *
import cv2
run_mgfpj_v3("./mgfpj_mcgpu1.jsonc")
run_mgfpj_v3("./mgfpj_mcgpu2.jsonc")
dtype1 = np.float32
num_slices = 720
folder3 = "E:/BaiduNetdiskDownload/homework/bone/sgm12"
column_lists = []
l1 = imreadRaw("C:/Users/p/Desktop/test/sgm_bone/sgm_water_modified.raw",512,512,nSlice=720)
l2 = imreadRaw("C:/Users/p/Desktop/test/sgm_bone/sgm_bone_modified.raw",512,512,nSlice=720)

with open('./Spectrum_110kVp1.txt', 'r') as file:  
    # 读取文件的每一行  
    for line in file:  
        # 去除每行末尾的换行符，并将字符串按某种分隔符（如空格或逗号）分割成列表  
        # 这里假设数据是用空格分隔的  
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

new_x = np.arange(20000, 110001, 1000)
# df4 = pd.read_excel('spec.xlsx')
x04 = np.array(column_lists[0])
y04 = np.array(column_lists[1])

f = interp1d(x04, y04, kind='linear')
new_y = f(new_x)
# print(x04)
x04 = new_x/1000
y04 = new_y

print(x04)
print(y04)

# print(column_lists)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from crip.io import imwriteRaw,imreadRaw
df1 = pd.read_excel('./pmma_u.xlsx')
x01 = df1['Energy(kev)'].values
y01 = df1['u'].values
x1 = np.log(x01)
y1 = np.log(y01) 
xi = [i for i in range(20, 101)]
xi = np.log(xi)
yi = np.interp(xi,x1,y1)
xi = np.exp(xi)
yi = np.exp(yi)

df2 = pd.read_excel('./fe_u.xlsx')
x02 = df2['Energy(kev)'].values
y02 = df2['u'].values
x2 = np.log(x02)
y2 = np.log(y02) 
xi = [i for i in range(20, 101)]
xi = np.log(xi)
yi2 = np.interp(xi,x2,y2)
xi = np.exp(xi)
yi2 = np.exp(yi2)






# print(x04.shape,y04.shape)
# array_2d1 = imreadRaw("./sgm_bone/sgm_water_modified.raw",h=512,w=512,dtype=np.float32,nSlice=720)
# array_2d2 = imreadRaw("./sgm_bone/sgm_bone_modified.raw",h=512,w=512,dtype=np.float32,nSlice=720)
lower = 0
higher = 0
for i in range(0,81):
    lower += y04[i]*x04[i]
for i in range(0,81):
    higher += y04[i]*x04[i]*np.exp(-1*yi[i]*l1*0.1-1*yi2[i]*l2*0.1*1.920)
    # higher += y04[i]*x04[i]*np.exp(-1*yi[i]*array_2d1*0.1)
    
primary = higher/lower
# imwriteRaw(result,"prelog_new.raw",dtype=np.float32)

# primary = imreadRaw("C:/Users/p/Desktop/test/sgm_bone/sgm_result1.raw",256,256,nSlice=720)


air_volume = np.zeros((40, 512, 512), dtype=dtype1)
for i in range(40):
    # filename = f"male_head_{i:04d}.raw"
    filename = f"air_{i+1}.raw"
    file3_path = os.path.join(folder3, filename)
    data3 = np.squeeze(imreadRaw(file3_path,512,512,nSlice=1,dtype=dtype1))
    data3 = data3[:, ::-1]  # 对每一行进行反转
    # 上下反转（垂直翻转）
    data3 = data3[::-1,:]
    air_volume[i] = data3
# imwriteRaw(primary,"./primary.raw",dtype=dtype1)
mean_array = np.mean(air_volume, axis=0)   # 在第一个维度取均值
scatter = np.zeros((720, 512, 512), dtype=dtype1)
total = np.zeros((720, 512, 512), dtype=dtype1)
folder3 = "E:/BaiduNetdiskDownload/homework/bone/sgm11"
# data1 = imreadRaw("E:/BaiduNetdiskDownload/homework/bone/primary_result.raw",512,256,nSlice=720,dtype=dtype1)
for i in range(num_slices):
    # filename = f"male_head_{i:04d}.raw"
    filename = f"bone_{i+1}.raw"
    file3_path = os.path.join(folder3, filename)
    data3 = np.squeeze(imreadRaw(file3_path,512,512,nSlice=2,dtype=dtype1)[1,:,:])
    data3 = data3[:, ::-1]  # 对每一行进行反转
    # 上下反转（垂直翻转）
    data3 = data3[::-1,:]
    kernel_size = (75,75)
    sigma = 10
    data3 = cv2.GaussianBlur(data3,kernel_size,sigma)
    # 相加后存入结果数组

    # resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)

    # result_volume[i] = -np.log((data1[i,:,:] - data2*10+data3*10)/1000)
    scatter[i] = data3/mean_array
    total[i] = scatter[i] + primary[i]
    total[i] = -np.log(total[i])
imwriteRaw(scatter,"./scatter.raw",dtype=dtype1)
imwriteRaw(primary,"./primary.raw",dtype=dtype1)
imwriteRaw(total,"./total.raw",dtype=dtype1)


    

