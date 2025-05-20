import os
import time
import numpy as np
"""
改为 20*20（10cm*10cm的小体积模体，并将附加材料改小）
"""
VoxSizeX = 100
VoxSizeZ = 100

# 体素物理尺寸（单位 cm）
VoxelSizeX = 0.1
VoxelSizeZ = 0.1
VoxelSizeY = 0.1

thickness_iodine_2 = 2
thickness_iodine_5 = 5
thickness_fe = 1
thickness_ta = 1
thickness_pt = 1
thickness_ba = 50
thickness_bone = 40
thickness_co2_2 = 2
thickness_co2_5 = 5

# 定义材料密度
density_air = 0.00120479  # 空气
density_pmma = 1.18  # PMMA
density_iodine = 0.35  # 碘块 (350 mg/mL)
density_fe = 7.874  # 铁
density_ta = 16.65  # 钽
density_pt = 21.45  # 铂
density_ba = 2  # 钡
density_bone = 1.92  # 骨骼
density_co2 = 0.001977  # CO₂

# 定义材料 ID
AirID = 1
PMMAID = 2
IodineID = 3
FeID = 4 # (用钢代替)
TaID = 5 # （用w代替 73->74）
PtID = 6 # (用钨替代 78->74)
BaID = 7 # （用碘化铯代替 csl）
BoneID = 8
CO2ID = 9 # （用空气）

# 输出文件夹（如果不存在）
output_dir = "/mnt/no2/huzhen/vox/miniMM"
# output_dir = "/Users/huzhen/Downloads"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def mainFunction(thickness_pmma):
    VoxSizeY = thickness_pmma + 50  # 以最大厚度为基准

    # 初始化体素空间
    mat_id = np.ones((VoxSizeX, VoxSizeY, VoxSizeZ), dtype=int) * AirID
    length_half = 5
    pmma_start_y = 50
    pmma_end_y = 50 + thickness_pmma

    # 设置碘2mm区域
    iodine_2_x = 75
    iodine_2_z = 50
    for y in range(0, thickness_iodine_2):
        for x in range(iodine_2_x-length_half, iodine_2_x + length_half):
            for z in range(iodine_2_z-length_half, iodine_2_z + length_half):
                mat_id[x, y, z] = IodineID

    # 设置碘5mm区域
    iodine_5_x = 72
    iodine_5_z = 66
    for y in range(0, thickness_iodine_5):
        for x in range(iodine_5_x - length_half, iodine_5_x + length_half):
            for z in range(iodine_5_z - length_half, iodine_5_z + length_half):
                mat_id[x, y, z] = IodineID

    # 设置Fe区域
    fe_x = 68
    fe_z = 35
    for y in range(0, thickness_fe):
        for x in range(fe_x - length_half, fe_x + length_half):
            for z in range(fe_z - length_half, fe_z + length_half):
                mat_id[x, y, z] = FeID

    # 设置Ta区域
    ta_x = 50
    ta_z = 80
    for y in range(0, thickness_ta):
        for x in range(ta_x - length_half, ta_x + length_half):
            for z in range(ta_z - length_half, ta_z + length_half):
                mat_id[x, y, z] = TaID

    # 设置Pt区域
    pt_x = 53
    pt_z = 25
    for y in range(0, thickness_pt):
        for x in range(pt_x - length_half, pt_x + length_half):
            for z in range(pt_z - length_half, pt_z + length_half):
                mat_id[x, y, z] = PtID

    # 设置Ba区域
    ba_x = 28
    ba_z = 66
    for y in range(0, thickness_ba):
        for x in range(ba_x - length_half, ba_x + length_half):
            for z in range(ba_z - length_half, ba_z + length_half):
                mat_id[x, y, z] = BaID

    # 设置Bone区域
    bone_x = 25
    bone_z = 50
    for y in range(0, thickness_bone):
        for x in range(bone_x - length_half, bone_x + length_half):
            for z in range(bone_z - length_half, bone_z + length_half):
                mat_id[x, y, z] = BoneID


    # 设置PMMA区域,整个纵截面
    mat_id[:, pmma_start_y:pmma_end_y, :] = PMMAID
    if(VoxSizeY >=60):
        # 设置Co2 2mm区域，需要嵌在内部
        co22_x = 28
        co22_z = 34
        startY = pmma_start_y+(thickness_pmma//2)-1
        endY = startY+ thickness_co2_2
        for y in range(startY, endY):
            for x in range(co22_x - length_half, co22_x + length_half):
                for z in range(co22_z - length_half, co22_z + length_half):
                    mat_id[x, y, z] = CO2ID

        # 设置Co2 5mm区域 嵌在内部
        co25_x = 37
        co25_z = 20
        startY -= 1
        endY = startY + thickness_co2_5
        for y in range(startY, endY):
            for x in range(co25_x - length_half, co25_x + length_half):
                for z in range(co25_z - length_half, co25_z + length_half):
                    mat_id[x, y, z] = CO2ID

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
        str(density_iodine),  # ID=3 => 碘块
        str(density_fe),  # ID=4 => 铁
        str(density_ta),  # ID=5 => 钽
        str(density_pt),  # ID=6 => 铂
        str(density_ba),  # ID=7 => 钡
        str(density_bone),  # ID=8 => 骨骼
        str(density_co2)  # ID=9 => CO₂
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
    vox_filename = f"{output_dir}/P{thickness_pmma}mm_Muti_QK.vox"
    with open(vox_filename, 'w') as fp:
        fp.writelines(vox_lines)  # 使用writelines直接写入列表

    # 记录结束时间
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Done writing {vox_filename}.")
    print(f"Execution time: {execution_time} seconds\n--------\n")

for pmma_thickness in range(50, 51, 10):
    mainFunction(pmma_thickness)
