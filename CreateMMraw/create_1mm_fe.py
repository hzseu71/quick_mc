import numpy as np
from pathlib import Path

# ── 初始化全 0 体数据 shape = (Z, Y, X) ─────────────────────────
def c_fe1(pmma_thickness):
    vol = np.zeros((450, 450, 450), dtype=np.float32)
    # 为了保持附加物在物体的相对探测器位置不变，在不同厚度下通过偏移值来调节新位置
    offset_p = 175



    # 取中心为 y,z,其中 x表达为厚度
    # shape = (Z, Y, X)

    # 3 Fe 1mm
    thickness = 1
    start_x = 450 - thickness
    y1,z1 = 68+offset_p,35+offset_p
    vol[z1-5:z1+5,y1-5:y1+5,start_x:450] = 1.0

    # ── 输出 .raw ─────────────────────────────────────────────────
    raw_path = Path(f"../raw/fe_1mm_523.raw")
    raw_path.write_bytes(vol.tobytes())
    print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")
