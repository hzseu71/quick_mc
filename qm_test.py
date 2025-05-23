import os
from pathlib import Path
import numpy as np
import pandas as pd
from crip.io import imreadRaw, imwriteRaw
from scipy.interpolate import interp1d
import cv2
from datetime import datetime

now = datetime.now()
month = now.month
day = now.day

pmma_thickness = 50

# debug 用
out_dir_test = Path("./test_raw")
out_dir_test.mkdir(exist_ok=True, parents=True)
'''
======================================
Part1 部分需要更改的配置
======================================
'''
dtype1      = np.float32          # 输出 dtype
RAW_SHAPE   = (300, 300)          # 每张 raw 的宽高（H, W）
ENERGY_GRID = np.arange(8, 101)  # keV，8–100 共 93 点,蒙卡最低要求8kev
MM2CM       = 0.1                 # 毫米 → 厘米
ENERGY_RANGE = 100
spectrum_file = 'spectrum100_Copper0.1mm.txt'


'''
======================================
Part2 部分需要更改的配置
======================================
'''
scatter_folder = r"./mcgpu/scat_raw"                  # mcgpu 图像输出目录
scatter_prefix = f"P{pmma_thickness}_muti_100kv_repeat_1_521_1"    # mcgpu模拟图像
AIR_PATH     = fr"./mcgpu/scat_raw/air/P{pmma_thickness}_muti_100kv_repeat_1_Air_521_1.raw"                   # 空气图像
round_num = 1
file_remarks = f'by_QM_{month}{day}_{round_num}'


'''
code part
======================================
'''

MATERIALS = {
    # 名称  (   密度 g/cm³ , μ(E)： Excel 路径 , 长度： raw 路径 )
    "pmma": ( 1.19, r"./attenuation_coefficient/pmma_u.xlsx", fr"./sgm/sgm_pmma_{pmma_thickness}mm_523.raw"),
    "fe"  : ( 3, r"./attenuation_coefficient/bone_u.xlsx"  , r"./sgm/sgm_fe_1mm_523.raw"),
    "iodine2":(3, r"./attenuation_coefficient/bone_u.xlsx", r"./sgm/sgm_iodine_2mm_523.raw"),
    "iodine5":(3, r"./attenuation_coefficient/bone_u.xlsx", r"./sgm/sgm_iodine_5mm_523.raw"),
    "ta"  : (3, r"./attenuation_coefficient/bone_u.xlsx"  , r"./sgm/sgm_ta_1mm_523.raw"),
    "pt"  : (3, r"./attenuation_coefficient/bone_u.xlsx"  , r"./sgm/sgm_pt_1mm_523.raw"),
    "ba"  : ( 3, r"./attenuation_coefficient/bone_u.xlsx"  , r"./sgm/sgm_ba_50mm_523.raw"),
    "bone": ( 3, r"./attenuation_coefficient/bone_u.xlsx", r"./sgm/sgm_bone_40mm_523.raw"),
    "co2_2" : ( 3, r"./attenuation_coefficient/bone_u.xlsx" , fr"./sgm/sgm_co2_2mm_P{pmma_thickness}mm_523.raw"),
    "co2_5" : ( 3, r"./attenuation_coefficient/bone_u.xlsx" , fr"./sgm/sgm_co2_5mm_P{pmma_thickness}mm_523.raw"),
}


#  1. 载入能谱并插值到 1 keV
spec_e_raw, spec_w_raw = np.loadtxt(f"./spectrum/{spectrum_file}", unpack=True)
interp = interp1d(spec_e_raw, spec_w_raw, kind='linear', bounds_error=False, fill_value=0)
spec_w = interp(ENERGY_GRID * 1_000)          # 把 keV→eV 再插值
spec_e = ENERGY_GRID                          # keV       (20…100)
spec_w /= spec_w.sum()                        # 若需要归一化，可取消注释


# 2. 为每种材料读取 μ(E) → 93 ×1 数组，读取厚度 raw → H×W
mu_dict   = {}   # key: material → (93,)
thick_dict = {}  # key: material → (H,W)

# 直接获得每个材料所对应的图像的密度、插值获得的μ/ρ(E)，和raw中记录的长度
for name, (rho, mu_xlsx, raw_path) in MATERIALS.items():
    # 2-1 μ(E) 插值到 ENERGY_GRID
    df = pd.read_excel(mu_xlsx)
    # mu_xlsx → 该材料的 μ/ρ(E) Excel 文件
    mu_interp = np.exp(np.interp(np.log(ENERGY_GRID),
                                 np.log(df['Energy(kev)'].values),
                                 np.log(df['u'].values)))

    # mu_dict 是全局 dict，key = 材料名，value = (93,) ndarray
    mu_dict[name] = mu_interp  # 长度 93

    # 2-2 厚度 map（mm）
    thick = imreadRaw(raw_path, *RAW_SHAPE, nSlice=1).astype(np.float32)
    # 给的正投影图不是三维的，下面关于三维的判断没必要
    # if thick.ndim == 3:
    #     thick = np.squeeze(thick, axis=0)  # 1×H×W → H×W
    thick_dict[name] = thick  # H×W

print("Loaded materials:", list(MATERIALS))


# 3. 计算 lower 与 higher

lower  = np.sum(spec_w * spec_e)             # 入射总能量 (标量),用numpy来加速积分过程
higher = np.zeros(RAW_SHAPE, dtype=np.float32)
for k, E_keV in enumerate(ENERGY_GRID):
    # 3-1 先算总线性衰减 μ·d (H×W)
    mu_t = np.zeros(RAW_SHAPE, dtype=np.float32)
    for name, (rho, _, _) in MATERIALS.items():
        mu   = mu_dict[name][k]              # 此能量点的 μ/ρ
        thick= thick_dict[name]              # mm
        mu_t += mu * rho * thick * MM2CM     # μ/ρ × ρ × t(cm)
    # 3-2 能量加权累加
    higher += spec_w[k] * spec_e[k] * np.exp(-mu_t)


# 4. 取透过率、Post-log，并写 raw
primary  = higher / lower


'''
======================================
part 2 散射信号叠加
======================================
'''
#
# # ── 0. 基本参数 ────────────────────────────────────────────────
# dtype1         = np.float32
# SCAT_SHAPE     = (300, 300)                     # (H, W) 本项目仅一张图,没有多余切片
# USE_AIR_FLAT   = False                          # 没有 AIR-flat 就设 False(对空气图做多张合成)
# sigma_px       = 5                             # 高斯核
#
# # ── 1. 读散射帧（取第 3 个切片）并左旋 90° ────────────────────
# nz = 1
# H, W  =SCAT_SHAPE          # 720 × 300 × 300
# scatter   = np.zeros(SCAT_SHAPE, dtype=dtype1)
#
# for i in range(nz):
#     fname = f"{scatter_prefix}.raw"
#     path  = os.path.join(scatter_folder, fname)
#
#     # ① 读取 (H, W, 3) → 取索引 2 作为散射层
#     slice3 = imreadRaw(path, H, W, nSlice=3, dtype=dtype1)[2]
#
#     # ② 左旋 90°（逆时针）——等价于 np.rot90(slice3, 1)
#     slice3 = cv2.rotate(slice3, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     # 若不用 OpenCV，可用： slice3 = np.rot90(slice3, 1)
#     imwriteRaw(slice3, out_dir_test / f"scatter_noGB_test.raw", dtype=dtype1)  # this code for debug
#     # ③ 可选：高斯平滑（低频化散射）
#     slice3 = cv2.GaussianBlur(slice3, (75,75), sigma_px)
#     imwriteRaw(slice3, out_dir_test / f"scatter_GB_test.raw", dtype=dtype1)  # this code for debug
#
#
#     scatter = slice3
#
# # ── 2. 读 AIR-flat 并做归一化 (当空气图光子量过低时用) ──────────────────────────
# if USE_AIR_FLAT:
#     air_vol = []
#     for f in sorted(os.listdir(AIR_PATH)):
#         if f.endswith(".raw"):
#             air_vol.append(imreadRaw(os.path.join(AIR_PATH, f), H, W, nSlice=1,
#                                      dtype=dtype1).squeeze())
#     mean_air = np.mean(np.stack(air_vol), axis=0) + 1e-6      # 防除零
#     scatter /= mean_air                                       # element-wise
#     del air_vol
# else:           # 使用单张空气图来完成逻辑
#     # 1) 读取单张 air：nSlice=3 取第1个切片,即带散射
#     air_img = imreadRaw(AIR_PATH, H, W, nSlice=3,
#                         dtype=dtype1)[0]
#
#     # 2) 做同样的几何处理——左旋 90°，保持坐标对应
#     air_img = cv2.rotate(air_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     imwriteRaw(air_img, out_dir_test / f"Air_noGB_test.raw", dtype=dtype1)  # this code for debug
#     air_img = cv2.GaussianBlur(air_img, (75, 75), sigma_px)
#     imwriteRaw(air_img, out_dir_test / f"Air_GB_test.raw", dtype=dtype1)  # this code for debug
#
#     # 3) 防除零；把散射归一化到 I/I0 量纲
#     air_img += 1e-6
#     scatter /= air_img
#     imwriteRaw(scatter, out_dir_test / f"scatter_ii0_test.raw", dtype=dtype1)  # this code for debug
#
# # out_dir = Path("./proj_with_scatter")
# # out_dir.mkdir(exist_ok=True, parents=True)
# # imwriteRaw(scatter, out_dir / f"test4.raw", dtype=dtype1)  # this code for debug
#
#
# # ── 3. 合并到 primary 并做 post-log ───────────────────────────
# # primary 在前面得到
# assert primary.shape == scatter.shape, "primary / scatter 尺寸不一致！"
#
# total   = -np.log(primary + scatter + 1e-6)      # 加小常数防 log0
postlog  = -np.log(primary + 1e-6)  # 对primary做postlog,已方便对比
# ── 4. 输出 ────────────────────────────────────────────────────
out_dir = Path("./proj_with_scatter")
out_dir.mkdir(exist_ok=True, parents=True)

imwriteRaw(primary, out_dir/f"P{pmma_thickness}_primary_muti_{ENERGY_RANGE}kv_by_QM_{month}{day}_{round_num}.raw", dtype=dtype1)
# imwriteRaw(scatter, out_dir/f"P{pmma_thickness}_scatter_muti_{ENERGY_RANGE}kv_by_QM_1.raw", dtype=dtype1)
# imwriteRaw(total,   out_dir/f"P{pmma_thickness}_total_muti_{ENERGY_RANGE}kv_by_QM_1.raw",   dtype=dtype1)
imwriteRaw(postlog, out_dir/f"P{pmma_thickness}_primary_to_postlog_muti_{ENERGY_RANGE}kv_by_QM_{month}{day}_{round_num}.raw", dtype=dtype1)

print("primary, primary_to_postlog 已写入", out_dir)