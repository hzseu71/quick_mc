import numpy as np
from pathlib import Path

def c_co2_2(pmma_thickness):
    # ── 初始化全 0 体数据 shape = (Z, Y, X) ─────────────────────────
    vol = np.zeros((450, 450, 450), dtype=np.float32)
    # 为了保持附加物在物体的相对探测器位置不变，在不同厚度下通过偏移值来调节新位置
    offset_p = 175




    # 取中心为 y,z,其中 x表达为厚度
    # shape = (Z, Y, X)

    # 1 co2 2mm
    y1,z1 = 28+offset_p,34+offset_p
    if pmma_thickness > 0:
        p_center = int(pmma_thickness / 2)
        vol[z1 - 5:z1 + 5, y1 - 5:y1 + 5, 400-p_center-1:400-p_center+1] = 1.0

    # ── 输出 .raw ─────────────────────────────────────────────────
    raw_path = Path(f"../raw/co2_2mm_P{pmma_thickness}mm_523.raw")
    raw_path.write_bytes(vol.tobytes())
    print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")
