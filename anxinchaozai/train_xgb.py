import pandas as pd
import xgboost as xgb
import os

def train_model():
    print(">> [2/3] 正在训练模型...")
    
    # [核心修改] 获取当前脚本所在文件夹的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'training_data.csv')
    model_path = os.path.join(current_dir, 'xgb_weight_model.json')

    if not os.path.exists(csv_path):
        print(f"错误：在 {csv_path} 未找到 training_data.csv")
        print("请确保 generate_data.py 和 train_xgb.py 在同一个文件夹，并先运行第一步。")
        return

    df = pd.read_csv(csv_path)
    
    X = df[['max_rpm', 'energy', 'duration', 'speed']]
    y = df['weight']
    
    model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1)
    model.fit(X, y)
    
    model.save_model(model_path)
    print(f">> 模型训练完成，已保存至: {model_path}")

if __name__ == "__main__":
    train_model()