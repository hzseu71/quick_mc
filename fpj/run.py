from crip.io import *
import numpy as np
import cv2

dtype1= np.float32
scatter= imreadRaw("./scatter.raw",512,512,nSlice=720,dtype=dtype1)
primary = imreadRaw("./primary.raw",512,512,nSlice=720,dtype=dtype1)
total = np.zeros((720, 512, 512), dtype=dtype1)
num_slices = 720
for i in range(num_slices):
    total[i] = scatter[i] + primary[i]
    total[i] = -np.log(total[i])

imwriteRaw(total,"./total.raw",dtype=dtype1)
from run_mgfbp import *

run_mgfbp("./config_mgfbp.jsonc")