import matplotlib.pyplot as plt
import numpy as np

# ✅ 设置支持中文的字体（根据系统换字体）
plt.rcParams['font.family'] = 'SimHei'  # Windows 示例
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 以下略：绘图代码同之前提供

# 示例数据
products = ['电磁阀组', '过滤器组', '薄型气缸', '先导', '单阀', '迷你缸']
demand = [3.1, 0.3, 0.4, 5.0, 5.0, 2.0]  # 产线需求数（虚拟数据）
capacity = [3000, 2000, 2200, 12000, 12000, 4000]  # 规划产能（件/班）

x = np.arange(len(products))
bar_width = 0.6

# 设置图像大小和 DPI
fig, ax1 = plt.subplots(figsize=(14, 7), dpi=100)

# 柱状图：产线需求数
bars = ax1.bar(x, demand, color='skyblue', width=bar_width, label='产线需求数', alpha=0.7)
ax1.set_ylabel('产线需求数', fontsize=13)
ax1.set_ylim(0, max(demand) + 1)

# 第二Y轴：折线图显示产能
ax2 = ax1.twinx()
line = ax2.plot(x, capacity, color='orange', marker='o', linewidth=2.5, markersize=8, label='规划产能（件/班）')
ax2.set_ylabel('规划产能（件/班）', fontsize=13, color='orange')
ax2.set_ylim(0, max(capacity) + 2000)

# 设置X轴
ax1.set_xticks(x)
ax1.set_xticklabels(products, fontsize=13)

# 标题
plt.title('各产品系列产线需求与规划产能对比图', fontsize=16, fontweight='bold', pad=15)

# 网格线
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# 图例
lines_labels = [bars, line[0]]
labels = [l.get_label() for l in lines_labels]
ax1.legend(lines_labels, labels, loc='upper left', fontsize=12)

# 调整边距
plt.tight_layout()

# 显示图形
plt.show()

plt.savefig("产线需求与产能对比图.png", bbox_inches='tight')
