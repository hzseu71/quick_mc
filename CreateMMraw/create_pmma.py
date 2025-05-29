import numpy as np
from pathlib import Path


'''
X是厚度！
'''
def c_pmma(pmma_thickness):
    # 构造体素数组：shape = (Z, Y, X)
    vol = np.zeros((450, 450, 450), dtype=np.float32)   # 全 0

    vol[:, :, 400-pmma_thickness:400] = 1.0
    # 刨去内嵌的co2位置
    offset_p = 175
    y1, z1 = 28 + offset_p, 34 + offset_p
    if pmma_thickness > 0:
        p_center = int(pmma_thickness / 2)
        vol[z1 - 5:z1 + 5, y1 - 5:y1 + 5, 400 - p_center - 1:400 - p_center + 1] = 0
    else:
        vol[z1 - 5:z1 + 5, y1 - 5:y1 + 5, 0:2] = 0
    y1, z1 = 37 + offset_p, 20 + offset_p
    if pmma_thickness > 0:
        p_center = int(pmma_thickness / 2)
        vol[z1 - 5:z1 + 5, y1 - 5:y1 + 5, 400 - p_center - 2:400 - p_center + 3] = 0
    else:
        vol[z1 - 5:z1 + 5, y1 - 5:y1 + 5, 0:5] = 0
    # 写成raw
    raw_path = Path(f"../raw/pmma/pmma_{pmma_thickness}mm_523.raw")
    raw_path.write_bytes(vol.tobytes())
    print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")