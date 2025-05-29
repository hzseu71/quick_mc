import cv2
import numpy as np
from crip.io import imreadRaw, imwriteRaw   # 如果用常规格式可改为 cv2.imread / cv2.imwrite

for round_num in range(10,19,1):
    # ── 0. 基本参数 ────────────────────────────────────────────────
    path1 = fr"../mcgpu/scat_raw/postlog/P30_postlog_mini_00{round_num}.raw"   # ← 第一幅图路径
    path2 = fr"../proj_with_scatter/P30_primary_to_postlog_Pm{round_num}.raw"   # ← 第二幅图路径
    H, W  = 300, 300            # ← 每张 raw 的高、宽
    dtype = np.float32          # ← 数据类型；若是 uint8 则改成 np.uint8


    # ── 1. 读入两幅图 ──────────────────────────────────────────────
    img1 = imreadRaw(path1, H, W, nSlice=1, dtype=dtype).squeeze()
    img2 = imreadRaw(path2, H, W, nSlice=1, dtype=dtype).squeeze()

    img1 = cv2.rotate(img1, cv2.ROTATE_180) # 旋转后才能和mgfpj对齐


    # ── 4. 做差值 ────────────────────────────────────────────────
    diff = img1 - img2                # dtype 仍为 float32
    diff = np.abs(diff)
    # ── 5. 保存结果（raw 或其它格式）──────────────────────────────
    imwriteRaw(diff, f"./diff_R{round_num}.raw", dtype=dtype)  # raw 二进制
    # 如要保存为 TIFF：cv2.imwrite("diff.tif", diff)（需转换到 uint16/8）
    print(f"Done! 差值已写入 diff_R{round_num}.raw")
