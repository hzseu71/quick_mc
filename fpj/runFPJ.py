import os
from crip.io import imreadRaw,imwriteRaw
import numpy as np

from run_mgfpj_v3 import *
import cv2
run_mgfpj_v3("./mgfpj_mcgpu3.jsonc")

from run_mgfbp import *
run_mgfbp("./mgfpj_mcgpu3.jsonc")