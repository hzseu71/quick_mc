import os
import subprocess

# 参数设置
spectrum_list = ['spectrum100_Copper0.1mm']
thickness_list = range(50, 401, 50)
repeat_count = 1
histories_per_run = 1e10
base_seed = 2342
file_remarks = 'Ba_607_e'
vox_remarks_list = ['Ba_606_2']
m_file_list = ['Ba']  # 如果你有多种材料，也可以在这里扩展

# 带中文注释的 MC-GPU 模板
template_content = """
{histories}                        # 模拟历史数（当值小于10万时表示模拟次数）
{seed}                             # 随机数种子（用于控制随机性，保证可重复）
0                                  # 使用的GPU编号（0 表示默认设备）
256                                # 每个CUDA块的线程数（必须是32的倍数）
1000                               # 每线程模拟的粒子数量

# ------------------ X射线源配置 ------------------
/mnt/no2/huzhen/spec/{spectrum}.txt      # 能谱文件路径（单位：keV）
5   -22.5   5                             # X射线源坐标 [X Y Z]，单位：cm
0.0    1.0    0.0                         # 源方向余弦 [U V W]
-1   -1                                   # 水平/垂直扇束角度 [度]，负数表示自动适配整个探测器
0  0   0                                   # 欧拉角旋转（通常为0）

# ------------------ 探测器设置 ------------------
/mnt/no2/huzhen/file_mc/P{thickness}_muti_100kv_repeat_{run}_{fileRemarks}     # 输出图像文件名（自动命名）
300    300                                 # 探测器像素数量 Nx x Nz
30     30                                 # 探测器物理尺寸 Dx x Dz（cm）
80                                       # 源到探测器距离（cm）
0.0    0.0                               # 探测器偏移 [cm]，默认居中
0.0200                                   # 探测器厚度（cm）
0.004027                                 # 探测器材料在平均能量下的平均自由程（cm）
0.05  3.51795                            # 防护盖厚度 & 平均自由程（polystyrene+detector）（cm）
130   90.55   0.00254                    # 防散射栅参数：比率、频率（lp/cm）、条带厚度（cm）
0.0157   1.2521                          # 栅条与间隙的平均自由程（lead & polystyrene）（cm）
1                                        # 防散射栅方向：1 表示栅条平行于侧向（DBT样式）

# ------------------ 轨迹/扫描设置 ------------------
1                                        # 投影数目（1表示单角度投影）
75                                       # 源到旋转轴的距离（cm）
90                                       # 相邻投影之间的角度（仅适用于CT）
0                                        # 第一角度偏移角（度）
0.0  0.0  1.0                            # 旋转轴方向向量 [Vx Vy Vz]
0.0                                      # 螺旋扫描时的轴向移动量（cm）

# ------------------ 模体体素文件 ------------------
/mnt/no2/huzhen/vox/QMVox/P{thickness}mm_Muti_QM_{vox}.vox       # 体素几何模型（.vox 格式）
0.0    0.0    0.0                            # 模体偏移位置 [cm]

# ------------------ 材料列表 ------------------
/mnt/no2/huzhen/material/air__5-120keV.mcgpu.gz                   # 空气
/mnt/no2/huzhen/material/PMMA__5-120keV.mcgpu.gz                 # PMMA（水等效材料）
/mnt/no2/huzhen/material/Se__5-120keV.mcgpu.gz                   # 探测器材料：硒
/mnt/no2/huzhen/material/steel__5-120keV.mcgpu.gz                # 钢（高Z材料示例）
/mnt/no2/huzhen/material/W__5-120keV.mcgpu.gz                    # 钨（用于栅条等）
/mnt/no2/huzhen/material/W__5-120keV.mcgpu.gz
/mnt/no2/huzhen/material/W__5-120keV.mcgpu.gz
/mnt/no2/huzhen/material/bone_ICRP110__5-120keV.mcgpu.gz         # 骨骼
/mnt/no2/huzhen/material/air__5-120keV.mcgpu.gz                  # 备用空气层
/mnt/no2/huzhen/material/Se__5-120keV.mcgpu.gz                   # 再次用于探测器
"""

# 创建并运行模拟
print("\n-------------------  MC-GPU 批处理启动  -------------------\n")

for spectrum in spectrum_list:
    print(f"\n开始处理能谱：{spectrum} --\n")
    for thickness in thickness_list:
        for vox_remarks in vox_remarks_list:
            for m_file in m_file_list:
                for run in range(1, repeat_count + 1):
                    seed = base_seed + run
                    histories = int(histories_per_run * (thickness / 200))

                    print(f"🟢 正在生成配置：{thickness}mm | run {run}")

                    # 替换模板内容
                    config_content = template_content.format(
                        spectrum=spectrum,
                        thickness=thickness,
                        seed=seed,
                        run=run,
                        histories=histories,
                        fileRemarks=file_remarks,
                        vox=vox_remarks,
                        mfile=m_file
                    )

                    # 写入 .in 配置文件
                    in_filename = f'config_{spectrum}_{thickness}mm_{vox_remarks}_run{run}.in'
                    with open(in_filename, 'w') as f:
                        f.write(config_content)

                    # 调用 MCGPULite 执行模拟
                    command = f'MCGPULite1.5 {in_filename}'
                    print(f'\n🚀 执行命令：{command}\n')
                    try:
                        subprocess.run(command, shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"❌ 模拟失败：{e}")
