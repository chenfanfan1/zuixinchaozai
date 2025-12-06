import pandas as pd
import xgboost as xgb
import os

def train_model():
    print(">> [2/3] 正在训练模型...")
    if not os.path.exists('训练.csv'):
        print("错误：未找到 训练.csv，请先运行第一步。")
        return

    df = pd.read_csv('训练.csv')
    
    # 特征与标签
    X = df[['max_rpm', 'energy', 'duration', 'speed']]
    y = df['weight']
    
    # 训练模型 (参数已优化)
    model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1)
    model.fit(X, y)
    
    # 保存
    model.save_model("XGBoost_weight_model.json")
    print(">> 模型训练完成: XGBoost_weight_model.json")

if __name__ == "__main__":
    train_model()