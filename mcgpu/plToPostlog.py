import numpy as np


def compute_postlog(projection_path, air_path, output_path,image_size):
    """
    计算投影图像的 Postlog 图。

    参数：
        projection_path (str): 投影图像路径 (I)，RAW 格式。
        air_path (str): 空气图像路径 (I0)，RAW 格式。
        output_path (str): 保存 Postlog 图的路径，RAW 格式。
    """
    # 图像尺寸和切片数定义
    # 图像尺寸
    num_slices = 3  # 总切片数

    # 加载 RAW 格式图像
    I = np.fromfile(projection_path, dtype=np.float32).reshape((num_slices, *image_size))
    I0 = np.fromfile(air_path, dtype=np.float32).reshape((num_slices, *image_size))

    # 只处理第一个切片
    I = I[1]
    I0 = I0[1]

    # 避免除以零
    epsilon = 1e-10  # 防止数值错误

    # 归一化处理：除空气图像
    I_prime = I / (I0 + epsilon)  # 归一化

    # 计算 Postlog 图：取负对数
    postlog_image = -np.log(I_prime + epsilon)  # 取负对数
    postlog_image[postlog_image < 0] = 0

    # 保存 Postlog 图为 RAW 格式
    postlog_image.astype(np.float32).tofile(output_path)

    print(f"Postlog 图已保存到: {output_path}\n")


# 示例用法
if __name__ == "__main__":
    air_image_path = "./scat_raw/air/Bone30_bone_Air_529_1.raw"  # 替换为空气图像的路径
    for pmma_thickness in range(30, 31, 10):
        projection_image_path = f"./scat_raw/P{pmma_thickness}_muti_100kv_repeat_1_muti_530_1.raw"  # 原始投影图像的路径
        output_postlog_path = f"./scat_raw/postlog/P{pmma_thickness}_postlog_muti_100kv_repeat_1_muti_530_1.raw"  # 替换为保存 Postlog 图的路径
        image_size = (300, 300)
        compute_postlog(projection_image_path, air_image_path, output_postlog_path,image_size)
