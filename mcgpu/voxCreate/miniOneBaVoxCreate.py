import os
import time
import numpy as np
"""
改为 20*20（10cm*10cm的小体积模体，并将附加材料改小）
Y 是厚度
"""
VoxSizeX = 30
VoxSizeZ = 30

# 体素物理尺寸（单位 cm）
VoxelSizeX = 0.1
VoxelSizeZ = 0.1
VoxelSizeY = 0.1


thickness_ba = 50


# 定义材料密度
density_air = 0.00120479  # 空气
density_pmma = 1.18  # PMMA
density_ba = 2*0.334*0.735*1.4  # 钡

# 定义材料 ID
AirID = 1
PMMAID = 2
BaID = 3 # (用钢代替)

# 输出文件夹（如果不存在）
output_dir = "./"
# output_dir = "/Users/huzhen/Downloads"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def mainFunction(thickness_pmma):
    VoxSizeY = thickness_pmma + 50  # 以最大厚度为基准

    # 初始化体素空间
    mat_id = np.ones((VoxSizeX, VoxSizeY, VoxSizeZ), dtype=int) * AirID
    length_half = 4
    pmma_start_y = 50
    pmma_end_y = 50 + thickness_pmma
    # 设置Ba区域
    ba_x = 15
    ba_z = 15
    for y in range(0, thickness_ba):
        for x in range(ba_x - length_half, ba_x + length_half):
            for z in range(ba_z - length_half, ba_z + length_half):
                mat_id[x, y, z] = BaID

    mat_id[:, pmma_start_y:pmma_end_y, :] = PMMAID

    # 生成 .vox 文件
    #    - 文件头：维度 & 体素尺寸 & 列信息
    #    - 每体素：材料ID & 对应材料的密度
    # -------------------------------------------------
    # 使用列表代替字符串拼接提高性能(空间换时间)
    vox_lines = []
    vox_lines.append("[SECTION VOXELS phantomER]\n")
    vox_lines.append(f"{VoxSizeX} {VoxSizeY} {VoxSizeZ} No. OF VOXELS IN X,Y,Z\n")
    vox_lines.append(f"{VoxelSizeX} {VoxelSizeY} {VoxelSizeZ} VOXEL SIZE(cm) ALONG X, Y, Z\n")
    vox_lines.append("1 COLUMN NUMBER WHERE MATERIAL ID IS LOCATED\n")
    vox_lines.append("2 COLUMN NUMBER WHERE THE MASS DENSITY IS LOCATED\n")
    vox_lines.append("0 BLANK LINES AT END OF X,Y-CYCLES (1=YES,0=NO)\n")
    vox_lines.append("[END OF VXH SECTION]\n")

    # 定义材料密度数组 Rhos
    Rhos = [
        None,  # 占位 (ID=0 不用)
        str(density_air),  # ID=1 => 空气
        str(density_pmma),  # ID=2 => PMMA
        str(density_ba)  # ID=4 => 铁
    ]

    # 预转换数据为列表（更高效）
    print(f"P{thickness_pmma}mm_MutipleMaterialsBot.vox start to write")

    # 记录开始时间
    start_time = time.time()
    mat_id_flat = mat_id.flatten()
    data_lines = []
    for mid in mat_id_flat:
        data_lines.append(f"{mid} {Rhos[mid]}\n")  # 直接追加格式化字符串

    # 合并所有行（比字符串拼接快约5-10倍）
    vox_lines += data_lines

    # 写入文件
    vox_filename = f"{output_dir}/P{thickness_pmma}mm_Ba_606_2.vox"
    with open(vox_filename, 'w') as fp:
        fp.writelines(vox_lines)  # 使用writelines直接写入列表

    # 记录结束时间
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Done writing {vox_filename}.")
    print(f"Execution time: {execution_time} seconds\n--------\n")

for pmma_thickness in range(300, 401, 10):
    mainFunction(pmma_thickness)
