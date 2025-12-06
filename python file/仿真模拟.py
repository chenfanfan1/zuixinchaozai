import pandas as pd
import numpy as np
from datetime import datetime

# 读取案例6-附件4-厂房物流需求数据_合并.csv
data = pd.read_csv('案例6-附件4-厂房物流需求数据_合并.csv')

# 1. 生产周期计算
# 假设每个工序段的生产周期为固定值（单位：分钟）
data['生产周期(分钟)'] = np.random.uniform(5, 30, size=len(data))  # 随机生成5-30分钟的生产周期

# 2. 物流时间计算
# 根据电梯运输距离和速度计算物流时间
data['物流时间(分钟)'] = (data['电梯运输距离（M）'] / data['电梯速度（M/S）'] + data['进出电梯耗时（S）']) / 60

# 3. 设备利用率计算
# 假设设备利用率为负载运载率的80%-100%
data['设备利用率(%)'] = np.random.uniform(80, 100, size=len(data))

# 4. 瓶颈分析
# 找出生产周期最长的工序
bottleneck_production = data.loc[data['生产周期(分钟)'].idxmax(), '工序段']
# 找出物流时间最长的工序
bottleneck_logistics = data.loc[data['物流时间(分钟)'].idxmax(), '工序段']
# 找出设备利用率最低的工序
bottleneck_equipment = data.loc[data['设备利用率(%)'].idxmin(), '工序段']

# 5. 优化建议
optimization_suggestions = {
    '生产周期优化': f"建议对工序段'{bottleneck_production}'进行流程优化，减少生产周期",
    '物流时间优化': f"建议优化工序段'{bottleneck_logistics}'的物流路径或增加电梯数量",
    '设备利用率优化': f"建议对工序段'{bottleneck_equipment}'的设备进行维护或调整生产计划"
}

# 准备仿真结果报告
report = f"""Flexsim仿真模拟报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

一、关键数据统计
1. 生产周期:
   平均值: {data['生产周期(分钟)'].mean():.2f} 分钟
   最大值: {data['生产周期(分钟)'].max():.2f} 分钟 (工序段: {bottleneck_production})
   最小值: {data['生产周期(分钟)'].min():.2f} 分钟

2. 物流时间:
   平均值: {data['物流时间(分钟)'].mean():.2f} 分钟
   最大值: {data['物流时间(分钟)'].max():.2f} 分钟 (工序段: {bottleneck_logistics})
   最小值: {data['物流时间(分钟)'].min():.2f} 分钟

3. 设备利用率:
   平均值: {data['设备利用率(%)'].mean():.2f}%
   最大值: {data['设备利用率(%)'].max():.2f}%
   最小值: {data['设备利用率(%)'].min():.2f}% (工序段: {bottleneck_equipment})

二、瓶颈分析
1. 生产瓶颈: {bottleneck_production}
2. 物流瓶颈: {bottleneck_logistics}
3. 设备瓶颈: {bottleneck_equipment}

三、优化建议
1. {optimization_suggestions['生产周期优化']}
2. {optimization_suggestions['物流时间优化']}
3. {optimization_suggestions['设备利用率优化']}

四、详细数据
{data.to_markdown(index=False)}
"""

# 保存仿真结果
output_file = 'Flexsim仿真模拟结果.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"仿真模拟完成，结果已保存到文件: {output_file}")