import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_facecolor('#f8f9fa')
ax.axis('off')

# 定义配色方案
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
titles = ['从至表', '关系图', '物流强度表']
features = [
    [r'$n \times n$ 矩阵，$x_{ij}$表示单位i→j的物流量'],
    ['不同线型表示关系强度：\nA级: ====（红色）\nE级: ≡≡≡（蓝色）'],
    ['基于帕累托法则\n前20%物流量定义为A级']
]

# 绘制信息卡片
card_height = 0.25
y_positions = [0.7, 0.4, 0.1]
for i, (title, color, feature, y) in enumerate(zip(titles, colors, features, y_positions)):
    # 绘制卡片背景
    ax.add_patch(mpatches.RoundedRectangle((0.1, y), 0.8, card_height, 
                  facecolor=color, edgecolor='none', alpha=0.9, radius=0.05))
    
    # 添加文字
    ax.text(0.5, y+card_height*0.65, title, ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    
    # 添加特征描述
    ax.text(0.5, y+card_height*0.3, feature[0], ha='center', va='center',
            fontsize=10, color='#2d3436')

# 添加线型示例
line_styles = [('A级', '====', 'red'), ('E级', '≡≡≡', 'blue')]
for i, (label, pattern, color) in enumerate(line_styles):
    ax.text(0.15, 0.45 - i*0.05, f'{label}:', color='black')
    line = Line2D([0.22, 0.3], [0.45 - i*0.05, 0.45 - i*0.05], 
                 linewidth=2, linestyle='-'*(len(pattern)//2), 
                 color=color)
    ax.add_line(line)

plt.tight_layout()
plt.savefig('infographic.png', dpi=300, bbox_inches='tight')
print("图表已保存为infographic.png")