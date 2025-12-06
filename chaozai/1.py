import numpy as np
import xgboost as xgb
import pandas as pd

class OverloadDetectionSystem:
    def __init__(self, model_path='xgb_weight_model.json'):
        # 1. 初始化系统参数
        self.threshold = 50       # STW-OSA 触发阈值 (例如编码器转速 RPM)
        self.window_buffer = []   # 用于存储时空窗内的数据
        self.is_recording = False # 状态标志位
        
        # 2. 加载预训练的 XGBoost 模型
        # 注意：实际使用前需要先训练模型并保存
        self.model = xgb.XGBRegressor()
        try:
            self.model.load_model(model_path)
            print(">> 系统模型加载成功")
        except:
            print(">> 警告：未找到预训练模型，系统处于全空模式")

    def process_realtime_stream(self, sensor_reading, car_speed):
        """
        模拟实时处理函数，该函数每10ms被调用一次
        :param sensor_reading: 当前时刻编码器的转速 (RPM)
        :param car_speed: 激光雷达测得的当前车速 (km/h)
        """
        
        # ==========================================
        # 阶段一：STW-OSA 在线序列分割算法
        # ==========================================
        
        # 逻辑A：触发条件 - 信号超过阈值，且当前未在记录
        if sensor_reading > self.threshold and not self.is_recording:
            self.is_recording = True
            self.window_buffer = [] # 清空缓存，开始新一段记录
            print(f"-> 检测到车辆进入，时空窗开启...")

        # 逻辑B：记录数据 - 如果处于记录状态
        if self.is_recording:
            self.window_buffer.append(sensor_reading)
            
            # 逻辑C：截断条件 - 信号回归平静 (简化逻辑：小于阈值)
            # 实际中通常需要判断"连续N个点小于阈值"以防噪声干扰
            if sensor_reading < self.threshold and len(self.window_buffer) > 10:
                self.is_recording = False
                print(f"-> 车辆离开，时空窗关闭。捕获样本点数: {len(self.window_buffer)}")
                
                # 触发后续处理流程
                self._analyze_and_predict(self.window_buffer, car_speed)

    def _analyze_and_predict(self, raw_data, speed):
        """
        内部处理函数：特征提取 -> 重量预测
        """
        
        # ==========================================
        # 阶段二：多维特征工程 (Feature Engineering)
        # ==========================================
        raw_array = np.array(raw_data)
        
        # 提取关键物理特征
        feature_max_rpm = np.max(raw_array)       # 1. 峰值转速 (反映冲击力)
        feature_energy = np.sum(raw_array)        # 2. 积分能量 (反映总做功)
        feature_duration = len(raw_array) * 0.01  # 3. 持续时间 (假设采样率100Hz)
        
        # 构建特征向量 X (需与训练时的输入格式一致)
        # 特征顺序: [Max_RPM, Energy, Duration, Speed]
        features = pd.DataFrame([[feature_max_rpm, feature_energy, feature_duration, speed]], 
                                columns=['max_rpm', 'energy', 'duration', 'speed'])
        
        print(f"   [特征提取] 峰值:{feature_max_rpm}, 能量:{feature_energy}, 持续:{feature_duration}s")

        # ==========================================
        # 阶段三：XGBoost 回归预测
        # ==========================================
        try:
            predicted_weight = self.model.predict(features)[0]
            self._judge_overload(predicted_weight)
        except Exception as e:
            print("   [错误] 模型预测失败 (可能是模型未训练)")

    def _judge_overload(self, weight):
        """
        决策输出
        """
        LIMIT = 49000 # 假设限重 49000 kg
        status = "正常" if weight <= LIMIT else "!!! 严重超载 !!!"
        print(f"   [结果输出] 预测重量: {weight:.2f} kg -> {status}")
        print("------------------------------------------------")

# ==========================================
# 模拟运行演示 (Mock Run)
# ==========================================
if __name__ == "__main__":
    # 实例化系统
    system = OverloadDetectionSystem()
    
    # 模拟一段传感器数据流 (包含噪声、一辆正常车、一辆超载车)
    # 0=噪声, 100-300=正常车, 500-800=超载车
    mock_data_stream = [0, 5, 0] * 10 + \
                       [100, 200, 300, 250, 100] + \
                       [0, 2, 0] * 10 + \
                       [500, 800, 900, 850, 600, 200] + \
                       [0, 0, 0]
    
    fixed_speed = 60.0 # 假设激光测得车速 60 km/h
    
    print("\n=== 系统开始实时监测 ===\n")
    for data_point in mock_data_stream:
        # 模拟每10ms传入一个数据
        system.process_realtime_stream(data_point, fixed_speed)