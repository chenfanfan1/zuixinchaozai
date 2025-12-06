import os
import numpy as np
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class OverloadDetectionSystem:
    def __init__(self, model_path='xgb_weight_model.json'):
        # 1. 初始化系统参数
        self.threshold = 50       # STW-OSA 触发阈值 (例如编码器转速 RPM)
        self.min_window_len = 3   # [修改点] 降低最小窗口长度限制，防止漏掉快速通过的车辆
        self.window_buffer = []   # 用于存储时空窗内的数据
        self.is_recording = False # 状态标志位

        # 记录与可视化相关
        self.sample_index = 0
        self.history = []         # 存所有传感器读数
        self.detections = []      # 存每次检测信息字典
        self.current_start_idx = None

        # 2. 加载预训练的 XGBoost 模型（增强健壮性）
        model_fullpath = model_path if os.path.isabs(model_path) else os.path.join(os.path.dirname(__file__), model_path)
        self.model = xgb.XGBRegressor()
        self.model_loaded = False
        try:
            self.model.load_model(model_fullpath)
            self.model_loaded = True
            print(f">> 系统模型加载成功: {os.path.basename(model_fullpath)}")
        except Exception as e:
            self.model_loaded = False
            print(">> 警告：未找到或无法加载预训练模型，系统处于全空模式。错误:", e)

    def process_realtime_stream(self, sensor_reading, car_speed):
        """
        模拟实时处理函数，该函数每10ms被调用一次
        :param sensor_reading: 当前时刻编码器的转速 (RPM)
        :param car_speed: 激光雷达测得的当前车速 (km/h)
        """

        # 记录时序数据用于画图
        self.history.append(sensor_reading)

        # ==========================================
        # 阶段一：STW-OSA 在线序列分割算法 (优化版)
        # ==========================================
        
        # 逻辑A: 触发开启
        if sensor_reading > self.threshold and not self.is_recording:
            self.is_recording = True
            self.window_buffer = []
            self.current_start_idx = self.sample_index
            print(f"-> [T={self.sample_index*0.01:.2f}s] 检测到车辆进入，时空窗开启...")

        # 逻辑B: 记录与闭合
        if self.is_recording:
            self.window_buffer.append(sensor_reading)

            # 逻辑C: 闭合条件 - 信号回归基线 (小于阈值)
            # [修改点] 这里的判断逻辑优化，确保波形结束后立即结算
            if sensor_reading < self.threshold:
                # 只有当收集的数据点足够多时才认为是有效车
                if len(self.window_buffer) > self.min_window_len:
                    self.is_recording = False
                    end_idx = self.sample_index
                    print(f"-> [T={self.sample_index*0.01:.2f}s] 车辆离开，时空窗关闭。捕获样本: {len(self.window_buffer)}")
                    # 触发分析
                    self._analyze_and_predict(self.window_buffer, car_speed, start_idx=self.current_start_idx, end_idx=end_idx)
                # 如果是极短的噪声脉冲，直接丢弃，重置状态
                elif len(self.window_buffer) <= self.min_window_len:
                     # 还在噪声范围内，暂不关闭，或者根据需求关闭但忽略
                     pass

        self.sample_index += 1

    def _analyze_and_predict(self, raw_data, speed, start_idx=None, end_idx=None):
        raw_array = np.array(raw_data)
        
        # 特征提取
        feature_max_rpm = np.max(raw_array)
        feature_energy = np.sum(raw_array)
        feature_duration = len(raw_array) * 0.01  # 假设采样率100Hz

        # 构造输入向量 (需与训练时一致)
        features = pd.DataFrame([[feature_max_rpm, feature_energy, feature_duration, speed]],
                                columns=['max_rpm', 'energy', 'duration', 'speed'])

        # 预测重量
        predicted_weight = 0.0
        if not getattr(self, "model_loaded", False):
            # 后备公式 (仅作演示)
            predicted_weight = feature_max_rpm * 18.0 + feature_energy * 0.4 + feature_duration * 1200.0 + speed * 4.5
            print(f"   [警告] 模型未加载，使用线性公式估算: {predicted_weight:.2f} kg")
        else:
            try:
                predicted_weight = float(self.model.predict(features)[0])
            except Exception as e:
                print("   [错误] 预测异常:", e)
                predicted_weight = 0.0

        # 保存检测结果
        det = {
            'id': len(self.detections) + 1,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'max_rpm': float(feature_max_rpm),
            'predicted_weight': float(predicted_weight),
            'is_overloaded': predicted_weight > 49000 # 假设限重49吨
        }
        self.detections.append(det)
        
        # 控制台输出
        status = "!!! 严重超载 !!!" if det['is_overloaded'] else "正常"
        print(f"   [结果] 预测重量: {predicted_weight:.2f} kg -> {status}")
        print("------------------------------------------------")

    def plot_results(self, save_path=None, sampling_rate=100):
        """
        [修改点] 全面升级的绘图函数 - 工业级仪表盘风格
        """
        if len(self.history) == 0:
            print("无数据可视化")
            return

        # 设置高颜值绘图风格
        try:
            plt.style.use('bmh') # 尝试使用 bmh 风格，如果没有则回退
        except:
            pass
            
        fig = plt.figure(figsize=(14, 10))
        # 创建布局：上部分是波形图(占2份)，下部分是柱状图(占1份)
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])

        # === 子图1：STW-OSA 传感器时域波形 ===
        ax1 = plt.subplot(gs[0])
        t = np.arange(len(self.history)) / sampling_rate
        
        # 绘制原始信号 (加一点透明度让网格透出来)
        ax1.plot(t, self.history, color='#2c3e50', linewidth=1.5, label='Rotary Encoder Speed (RPM)')
        
        # 绘制阈值线
        ax1.axhline(y=self.threshold, color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Trigger Threshold ({self.threshold})')

        # 标注检测到的窗口
        limit_weight = 49000
        for d in self.detections:
            if d['start_idx'] is None: continue
            
            # 时间转换
            t_start = d['start_idx'] / sampling_rate
            t_end = d['end_idx'] / sampling_rate
            t_mid = (t_start + t_end) / 2
            
            # 根据是否超载决定颜色 (绿=正常，红=超载)
            color = '#e74c3c' if d['is_overloaded'] else '#2ecc71'
            fill_color = '#c0392b' if d['is_overloaded'] else '#27ae60'
            
            # 绘制检测区间背景
            ax1.axvspan(t_start, t_end, color=fill_color, alpha=0.2)
            
            # 标注峰值点
            peak_val = d['max_rpm']
            ax1.scatter(t_mid, peak_val, color=color, s=50, zorder=5, edgecolors='white')
            
            # 标注文字 (车ID + 重量)
            label_text = f"Car #{d['id']}\n{d['predicted_weight']/1000:.1f}t"
            ax1.text(t_mid, peak_val + 50, label_text, ha='center', va='bottom', fontsize=9, fontweight='bold', color=color)

        ax1.set_title('Real-time Sensor Data Stream & STW-OSA Segmentation', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('Rotation Speed (RPM)', fontsize=12)
        ax1.set_xlabel('Time (seconds)', fontsize=12)
        ax1.legend(loc='upper right', frameon=True)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(bottom=-50) # 留一点底部空间

        # === 子图2：XGBoost 重量预测结果对比 ===
        ax2 = plt.subplot(gs[1])
        
        if len(self.detections) > 0:
            ids = [f"#{d['id']}" for d in self.detections]
            weights = [d['predicted_weight'] for d in self.detections]
            colors = ['#e74c3c' if d['is_overloaded'] else '#2ecc71' for d in self.detections]
            
            bars = ax2.bar(ids, weights, color=colors, alpha=0.85, width=0.5)
            
            # 绘制限重红线
            ax2.axhline(y=limit_weight, color='#c0392b', linewidth=2, linestyle='-', label='Legal Limit (49t)')
            
            # 在柱子上标数值
            for bar, w, d in zip(bars, weights, self.detections):
                height = bar.get_height()
                status_icon = "(!)" if d['is_overloaded'] else "(OK)"
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1000,
                         f'{w/1000:.1f} t\n{status_icon}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
            
            ax2.legend(loc='upper right')
        else:
            ax2.text(0.5, 0.5, "No Vehicles Detected Yet", ha='center', va='center', fontsize=14, color='gray')

        ax2.set_title('XGBoost Weight Estimation Results', fontsize=14, fontweight='bold', pad=15)
        ax2.set_ylabel('Estimated Weight (kg)', fontsize=12)
        ax2.set_ylim(0, max(weights + [60000]) * 1.2 if len(self.detections) > 0 else 10000)
        ax2.grid(axis='y', alpha=0.3)

        # 调整布局防止重叠
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f">> 可视化图表已保存至: {save_path}")
        plt.show()


if __name__ == "__main__":
    system = OverloadDetectionSystem()
    
    # [修改点] 增强版模拟数据生成：加入噪声和尾部静默区
    np.random.seed(42)
    
    # 1. 基础噪声 (模拟传感器抖动)
    noise_level = 5
    background_noise = np.random.normal(0, noise_level, 100)
    
    # 2. 正常车辆信号 (W0) - 峰值约300
    car1_signal = np.concatenate([
        np.linspace(0, 300, 20), 
        np.linspace(300, 0, 20)
    ]) + np.random.normal(0, noise_level, 40)
    
    # 3. 超载车辆信号 (W1) - 峰值约900，更宽，更猛
    car2_signal = np.concatenate([
        np.linspace(0, 900, 30), 
        np.linspace(900, 800, 10), # 机械回弹震荡
        np.linspace(800, 0, 30)
    ]) + np.random.normal(0, noise_level, 70)
    
    # 4. 组合数据流
    # [重要] 最后必须加一段 zeros，让 STW 算法有机会检测到波形结束并闭合窗口！
    mock_data_stream = np.concatenate([
        background_noise,       # 前段噪声
        car1_signal,            # 车1
        np.zeros(30),           # 间隔
        car2_signal,            # 车2 (超载)
        np.zeros(50)            # [修复漏检] 尾部静默区，确保最后一个窗口能闭合
    ])
    
    # 简单的绝对值处理(模拟整流后效果)并取整
    mock_data_stream = np.abs(mock_data_stream).astype(int)
    
    fixed_speed = 60.0 # 假设车速

    print("\n=== 系统开始实时监测 (模拟运行) ===\n")
    for data_point in mock_data_stream:
        system.process_realtime_stream(data_point, fixed_speed)

    # 运行结束后绘图
    output_img = os.path.join(os.path.dirname(__file__), 'detection_dashboard.png')
    system.plot_results(save_path=output_img)