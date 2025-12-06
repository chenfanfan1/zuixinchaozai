import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 模拟案例6-附件4表6-4的数据结构
data = {
    '时间戳': pd.date_range('2025-05-13 08:00', periods=200, freq='T'),
    'X坐标': np.random.randint(0, 100, 200),
    'Y坐标': np.random.randint(0, 50, 200),
    '冲突类型': np.random.choice(['路径交叉', '等待超时', '避让延迟'], 200, p=[0.6, 0.3, 0.1])
}

df = pd.DataFrame(data)

# 生成基础热力图
plt.figure(figsize=(12, 6))
heatmap_data = df.groupby(['X坐标', 'Y坐标']).size().unstack(fill_value=0)
sns.heatmap(heatmap_data, 
           cmap='YlOrRd',
           annot=True,
           fmt="d",
           linewidths=.5,
           cbar_kws={'label': '冲突次数'})

plt.title("AGV路径冲突热力图（案例6-附件4数据）")
plt.xlabel("X坐标（米）")
plt.ylabel("Y坐标（米）")
plt.savefig('agv_conflict_heatmap.png', dpi=300)
plt.show()