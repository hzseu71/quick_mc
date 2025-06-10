import numpy as np
from pathlib import Path


'''
X是厚度！
'''

# 构造体素数组：shape = (Z, Y, X)
vol = np.zeros((450, 450, 450), dtype=np.float32)   # 全 0
vol[:, :, :] = 1.0
# 写成raw
raw_path = Path(f"../raw/air_607.raw")
raw_path.write_bytes(vol.tobytes())
print("Saved", raw_path, "| shape", vol.shape, "| dtype=float32")