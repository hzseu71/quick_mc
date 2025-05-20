#!/usr/bin/env python3
"""
make_block_20x20x70_raw.py
--------------------------
体素尺寸 (X,Y,Z) = (20, 20, 70)
slice Z = 0 上，方块中心 (12,15)，方块大小 2×2 → 值 = 1
其余体素 = 0
输出： phantom_block_20x20x70.raw
"""

import numpy as np
from pathlib import Path

# ── 初始化全 0 体数据 shape = (Z, Y, X) ─────────────────────────
vol = np.zeros((100, 100, 100), dtype=np.float32)

# ── 在第 0 层 (Z=0) 写入 2×2 方块 ──────────────────────────────
# 取中心 (x0, y0) = (12, 15)；实际索引 0-based
y0 = 50
vol[40:60, y0-10:y0+10,75 ] = 1.0     # 2×2 像素 → 值 1

# ── 输出 .raw ─────────────────────────────────────────────────
raw_path = Path("raw/fe_1mm_n.raw")
raw_path.write_bytes(vol.tobytes())
print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")
