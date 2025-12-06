import pandas as pd
import numpy as np
import os

def generate_dataset():
    print(">> [1/3] 正在生成逻辑咬合的训练数据...")
    np.random.seed(42)
    N_SAMPLES = 10000
    
    # 1. 模拟重量分布
    weights = np.exp(np.random.uniform(np.log(2000), np.log(100000), N_SAMPLES))
    
    # 2. 模拟车速
    speeds = np.random.uniform(10, 100, N_SAMPLES)
    
    # 3. 建立物理关联 (系数 15.0)
    base_rpm = weights / 15.0 
    max_rpm = base_rpm * np.random.uniform(0.95, 1.05, N_SAMPLES)
    
    duration = (15.0 / speeds) * np.random.uniform(0.9, 1.1, N_SAMPLES)
    energy = (weights * 0.5) * duration * np.random.uniform(0.9, 1.1, N_SAMPLES)
    
    df = pd.DataFrame({
        'max_rpm': max_rpm.astype(int),
        'energy': energy.astype(int),
        'duration': duration.round(3),
        'speed': speeds.round(1),
        'weight': weights.astype(int)
    })
    
    df = df[df['max_rpm'] > 0]
    
    # [核心修改] 获取当前脚本所在文件夹的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'training_data.csv')
    
    df.to_csv(file_path, index=False)
    print(f">> 数据生成完成，已保存至: {file_path}")

if __name__ == "__main__":
    generate_dataset()