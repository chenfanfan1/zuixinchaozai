print("hello world")
print("suxxxux")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
print(np.__version__)
print(pd.__version__)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

# 声明全局变量用于存储图像标题
_mfajlsdf98q21_image_title_list = []

# 创建示例数据
# 生成x和y的网格点
x = np.linspace(0, 10, 50)
y = np.linspace(0, 10, 50)
X, Y = np.meshgrid(x, y)

# 创建风险值z (示例函数：风险值由两个风险因素共同决定)
# 这里使用二次函数来模拟风险随因素增加而非线性增长的情况
Z = 2 * (X - 5)**2 + 1.5 * (Y - 5)**2 + 0.5 * X * Y * np.sin(X) - 10

# 创建图形
fig = plt.figure(figsize=(12, 10))

# 添加3D热力图
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=0, antialiased=False)

# 设置坐标轴标签
ax.set_xlabel('Risk Factor 1')
ax.set_ylabel('Risk Factor 2')
ax.set_zlabel('Risk Level')

# 添加颜色条
cbar = fig.colorbar(surf, ax=ax, shrink=0.7, aspect=10)
cbar.set_label('Risk Intensity')

# 设置图表标题
title = '3D Risk Heat Map'
plt.title(title)
_mfajlsdf98q21_image_title_list.append(title)

# 调整视角以获得更好的3D效果
ax.view_init(elev=30, azim=45)

# 显示网格
ax.grid(True)

# 显示图像
plt.tight_layout()
plt.show()