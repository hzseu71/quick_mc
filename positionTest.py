import matplotlib.pyplot as plt
import numpy as np

# 图像大小
fig_size = 450
center_x, center_y = fig_size / 2, fig_size / 2

# 矩形参数
rect_size = 10
num_rects = 9
radius = 25  # 保持原始间距（从100×100图复制过来）

# 创建图形
fig, ax = plt.subplots(figsize=(6, 6))  # 图像比例为 1:1
ax.set_xlim(0, fig_size)
ax.set_ylim(0, fig_size)
ax.set_aspect('equal')
ax.set_title("9 Rectangles in Circular Layout", fontsize=14)

# 绘制矩形
for i in range(num_rects):
    angle = 2 * np.pi * i / num_rects
    # 相对于中心的偏移量
    dx = radius * np.cos(angle)
    dy = radius * np.sin(angle)

    # 中心坐标
    cx = center_x + dx
    cy = center_y + dy
    print(cx, cy)
    print("\n")
    # 左下角坐标 = 中心减去一半大小
    rect = plt.Rectangle(
        (cx - rect_size / 2, cy - rect_size / 2),
        rect_size,
        rect_size,
        edgecolor='blue',
        facecolor='skyblue'
    )
    ax.add_patch(rect)
    # 可选：显示中心编号
    ax.text(cx, cy, str(i), fontsize=8, ha='center', va='center', color='black')

# 去掉坐标轴
ax.axis('off')

# 显示图像
plt.tight_layout()
plt.show()
