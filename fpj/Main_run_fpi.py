import json
from run_mgfpj_v3 import run_mgfpj_v3

# 🧩 扫描编号统一设置
SCAN_SUFFIX = "530"  # 只需在此处修改，如改为 "600"

# 🧪 原始材料前缀（不要带 .raw 后缀）
material_names = [
    "pmma_30mm",
    "ba_50mm",
    "bone_40mm",
    "fe_1mm",
    "iodine_2mm",
    "iodine_5mm",
    "pt_1mm",
    "ta_1mm",
    "co2_2mm_P30mm",
    "co2_5mm_P30mm"
]

# ⛏ 构造完整的 raw 文件名列表
raw_files = [f"{name}_{SCAN_SUFFIX}.raw" for name in material_names]

# 🔧 内嵌 JSON 配置模板
base_config = {
    "InputDir": "../raw/",
    "OutputDir": "../sgm/",
    "InputFiles": "",
    "OutputFilePrefix": "",
    "OutputFileReplace": ["", ""],
    "ImageDimension": 450,
    "PixelSize": 1,
    "ImageDimensionZ": 450,
    "VoxelHeight": 1,
    "ConeBeam": True,
    "SourceIsocenterDistance": 450,
    "SourceDetectorDistance": 800,
    "StartAngle": 0,
    "DetectorElementCountHorizontal": 300,
    "Views": 1,
    "TotalScanAngle": 360,
    "DetectorElementCountVertical": 300,
    "DetectorElementWidth": 1,
    "DetectorOffsetHorizontal": 0,
    "DetectorOffsetVertical": 0,
    "DetectorElementHeight": 1,
    "OversampleSize": 1,
    "ForwardProjectionStepSize": 0.001,
    "OutputFileForm": "post_log_images",
    "ImageRotation": 0
}

for filename in raw_files:
    print(f"\n🚀 正在模拟：{filename}")
    material_prefix = filename.split("_")[0] + "_"  # 如 "ba_"

    # 修改配置项
    config = base_config.copy()
    config["InputFiles"] = filename
    config["OutputFileReplace"] = [material_prefix, f"sgm_{material_prefix}"]

    # 写入临时 JSON 文件
    temp_config_path = "temp_mgfpj.jsonc"
    with open(temp_config_path, "w") as f:
        json.dump(config, f, indent=2)

    # 执行模拟
    run_mgfpj_v3(temp_config_path)

print("\n✅ 所有模拟完成！")
