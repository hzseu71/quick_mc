import os
from pathlib import Path
import numpy as np
import pandas as pd
from crip.io import imreadRaw, imwriteRaw
from scipy.interpolate import interp1d

dtype1      = np.float32          # 输出 dtype
RAW_SHAPE   = (300, 300)          # 每张 raw 的宽高（H, W）
ENERGY_GRID = np.arange(8, 101)  # keV，8–100 共 93 点,蒙卡最低要求8kev
MM2CM       = 0.1                 # 毫米 → 厘米

MATERIALS = {
    # 名称  (   密度 g/cm³ , μ(E)： Excel 路径 , 长度： raw 路径 )
    "pmma": ( 1.19, r"./attenuation_coefficient/pmma_u.xlsx", r"./sgm/sgm_pmma_50mm_516_1.raw"),
    "fe"  : ( 7.87, r"./attenuation_coefficient/fe_u.xlsx"  , r"./sgm/sgm_fe_1mm_516.raw"),
    "iodine2":(4.93, r"./attenuation_coefficient/iodine_u.xlsx", r"./sgm/sgm_iodine_2mm_516.raw"),
    "iodine5":(4.93, r"./attenuation_coefficient/iodine_u.xlsx", r"./sgm/sgm_iodine_5mm_516.raw"),
    "ta"  : (16.69, r"./attenuation_coefficient/ta_u.xlsx"  , r"./sgm/sgm_ta_1mm_516.raw"),
    "pt"  : (21.45, r"./attenuation_coefficient/pt_u.xlsx"  , r"./sgm/sgm_pt_1mm_516.raw"),
    "ba"  : ( 3.62, r"./attenuation_coefficient/ba_u.xlsx"  , r"./sgm/sgm_ba_50mm_516.raw"),
    "bone": ( 1.85, r"./attenuation_coefficient/bone_u.xlsx", r"./sgm/sgm_bone_40mm_516.raw"),
    "co2_2" : ( 8.90, r"./attenuation_coefficient/co2_u.xlsx" , r"./sgm/sgm_co2_2mm_P50mm_516.raw"),
    "co2_5" : ( 8.90, r"./attenuation_coefficient/co2_u.xlsx" , r"./sgm/sgm_co2_5mm_P50mm_516.raw"),
}

#  1. 载入能谱并插值到 1 keV
spec_e_raw, spec_w_raw = np.loadtxt("./spectrum/spectrum100_Copper0.1mm.txt", unpack=True)
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
postlog  = -np.log(primary + 1e-6)

out_dir = Path("./result_raw")
out_dir.mkdir(exist_ok=True)
imwriteRaw(primary, out_dir/"primary_multi_517_1.raw", dtype=dtype1)
imwriteRaw(postlog, out_dir/"primary_multi_postlog_517_1.raw", dtype=dtype1)
print("Saved:", out_dir/"primary_multi_postlog.raw", "| shape", postlog.shape)