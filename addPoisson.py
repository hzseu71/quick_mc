import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter
from crip.io import imreadRaw, imwriteRaw  # 可替换成 numpy 自定义函数

# === 参数设置 ===
H, W = 300, 300                 # 图像尺寸
dtype = np.float32
photon_in = 1e6               # 入射光子数
gaussian_sigma = 5           # 高斯滤波标准差

# === 路径设置 ===
primary_path       = Path("./proj_with_scatter/P30_primary_muti_100kv_by_QM_64_2.raw")
scatter_path       = Path("./mcgpu/scat_raw/P30_muti_610_a.raw")
air_primary_path   = Path("./proj_with_scatter/Air_primary_muti_100kv_by_QM_67_1.raw")
air_scatter_path   = Path("./mcgpu/scat_raw/air/P30_muti_100kv_repeat_1_Air.raw")

output_poisson_path = Path("./poisson/output_poisson_G5_H1e6.raw")
output_postlog_path = Path("./poisson/output_postlog_poisson_G5_H1e6.raw")
output_scatter_path = Path("./poisson/output_scatter_G5_H1e6.raw")
output_t_path = Path("./poisson/output_t_8.raw")
# === 读入图像 ===
primary          = imreadRaw(str(primary_path), H, W, nSlice=1, dtype=dtype).squeeze()
scatter_full     = imreadRaw(str(scatter_path), H, W, nSlice=3, dtype=dtype).squeeze()
air_primary      = imreadRaw(str(air_primary_path), H, W, nSlice=1, dtype=dtype).squeeze()
air_scatter_full = imreadRaw(str(air_scatter_path), H, W, nSlice=3, dtype=dtype).squeeze()

scatter      = scatter_full[2]                 # 第3张切片
scatter      = np.rot90(scatter, k=1)          # 左旋90°
air_scatter  = air_scatter_full[0]

# === 高斯滤波 ===
scatter_filtered = gaussian_filter(scatter, sigma=gaussian_sigma)
imwriteRaw(scatter_filtered,str(output_scatter_path), dtype=dtype)
# === 步骤1：归一化 Primary 与 Scatter 图像 ===
norm_primary = primary / (air_primary + 1e-6)
norm_scatter = scatter_filtered / (air_scatter + 1e-6)

# === 步骤2：计算透过光子数 ===
total_transmission = (norm_primary + norm_scatter) * photon_in
imwriteRaw(total_transmission,str(output_t_path), dtype=dtype)
# === 步骤3：加入泊松噪声 ===
poisson_noisy = np.random.poisson(total_transmission).astype(dtype)

# === 步骤4：计算带噪声后的 Postlog 图像 ===
postlog_with_noise = -np.log((poisson_noisy + 1e-6) / photon_in)

# === 步骤5：保存图像 ===
imwriteRaw(poisson_noisy, str(output_poisson_path), dtype=dtype)
imwriteRaw(postlog_with_noise, str(output_postlog_path), dtype=dtype)

print(f"[✓] 已保存带泊松噪声图像: {output_poisson_path}")
print(f"[✓] 已保存对应的 Postlog 图像: {output_postlog_path}")
