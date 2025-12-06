import pandas as pd
import numpy as np

def generate_dataset():
    print(">> [1/3] 正在生成逻辑咬合的训练数据...")
    np.random.seed(42)
    N_SAMPLES = 10000
    
    # 1. 模拟重量分布：2吨 - 100吨 (涵盖小车到百吨王)
    # 使用对数分布，模拟真实世界中轻车多、重车少的情况
    weights = np.exp(np.random.uniform(np.log(2000), np.log(100000), N_SAMPLES))
    
    # 2. 模拟车速：10 - 100 km/h
    speeds = np.random.uniform(10, 100, N_SAMPLES)
    
    # 3. [关键逻辑] 建立物理关联
    # 设定核心系数：15.0。即：1500 RPM 对应 22.5吨左右。
    # 只有确定了这个系数，后面的演示代码才能造出准确重量的车。
    base_rpm = weights / 15.0 
    
    # 加入非线性扰动 (模拟传感器误差 + 机械阻力)
    max_rpm = base_rpm * np.random.uniform(0.95, 1.05, N_SAMPLES)
    
    # 能量积分与持续时间
    duration = (15.0 / speeds) * np.random.uniform(0.9, 1.1, N_SAMPLES)
    energy = (weights * 0.5) * duration * np.random.uniform(0.9, 1.1, N_SAMPLES)
    
    # 保存 CSV
    df = pd.DataFrame({
        'max_rpm': max_rpm.astype(int),
        'energy': energy.astype(int),
        'duration': duration.round(3),
        'speed': speeds.round(1),
        'weight': weights.astype(int)
    })
    
    # 过滤异常值
    df = df[df['max_rpm'] > 0]
    df.to_csv('训练.csv', index=False)
    print(f">> 数据生成完成: 训练.csv ({len(df)}条)")

if __name__ == "__main__":
    generate_dataset()