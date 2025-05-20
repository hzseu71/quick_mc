#!/usr/bin/env python3
"""
make_20x20x70_raw.py
--------------------
( X, Y, Z ) = (20, 20, 70)
Z = 0‥49  → value = 0
Z = 50‥69 → value = 1
输出：phantom_20x20x70.raw  （32-bit float, little-endian）
"""

import numpy as np
from pathlib import Path



pmma_thickness = 400
# 构造体素数组：shape = (Z, Y, X)
vol = np.zeros((450, 450, 450), dtype=np.float32)   # 全 0
vol[:, 175:275, 400-pmma_thickness:400] = 1.0                             # 后 20 slice 置 1

# 写成raw
raw_path = Path("./raw/pmma_400mm_516_1.raw")
raw_path.write_bytes(vol.tobytes())
print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")
