import os
import numpy as np
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class OverloadDetectionSystem:
    def __init__(self, model_path='xgb_weight_model.json'):
        self.threshold = 50       
        self.min_window_len = 3   
        self.window_buffer = []   
        self.is_recording = False 
        self.history = []         
        self.detections = []      
        self.current_start_idx = None
        self.sample_index = 0

        # 加载 AI 模型
        self.model = xgb.XGBRegressor()
        self.model_loaded = False
        try:
            self.model.load_model(os.path.join(os.path.dirname(__file__), model_path))
            self.model_loaded = True
            print(">> 模型加载成功")
        except:
            print(">> [模拟模式] 模型加载失败或文件不存在")

        # === [新增] 法定限重标准库 (GB 1589-2016) ===
        # 模拟数据库：根据车型/轴数返回限重(kg)
        self.LIMIT_DATABASE = {
            "2-Axle": 18000, # 两轴货车
            "3-Axle": 25000, # 三轴货车
            "4-Axle": 31000, # 四轴货车
            "6-Axle": 49000  # 六轴半挂 (百吨王通常是这类)
        }

    def process_realtime_stream(self, sensor_reading, car_speed, simulated_vehicle_type=None):
        """ 
        :param simulated_vehicle_type: 模拟摄像头传来的车型数据 (仅用于演示)
        """
        self.history.append(sensor_reading)

        if sensor_reading > self.threshold and not self.is_recording:
            self.is_recording = True
            self.window_buffer = []
            self.current_start_idx = self.sample_index
            # [模拟] 记录当前通过车辆的类型 (暂存)
            self.current_car_type = simulated_vehicle_type
            
        if self.is_recording:
            self.window_buffer.append(sensor_reading)
            if sensor_reading < self.threshold: 
                if len(self.window_buffer) > self.min_window_len:
                    self.is_recording = False
                    end_idx = self.sample_index
                    # 触发分析，传入车型
                    self._analyze_and_predict(self.window_buffer, car_speed, 
                                            start_idx=self.current_start_idx, end_idx=end_idx,
                                            vehicle_type=self.current_car_type)
        self.sample_index += 1

    def _analyze_and_predict(self, raw_data, speed, start_idx, end_idx, vehicle_type):
        raw_array = np.array(raw_data)
        
        # 1. 特征提取
        feature_max_rpm = np.max(raw_array)
        feature_energy = np.sum(raw_array)
        feature_duration = len(raw_array) * 0.01 

        # 2. AI 预测
        features = pd.DataFrame([[feature_max_rpm, feature_energy, feature_duration, speed]],
                                columns=['max_rpm', 'energy', 'duration', 'speed'])
        
        if self.model_loaded:
            try:
                predicted_weight = float(self.model.predict(features)[0])
            except:
                predicted_weight = 0.0
        else:
            # 仅作演示时的兜底，确保有数据画图
            predicted_weight = feature_max_rpm * 15 + 2000 

        # 3. [核心] 动态阈值判定 logic
        # 如果摄像头没识别到(None)，默认按最严的或者最宽的判，这里假设默认6轴
        v_type = vehicle_type if vehicle_type else "6-Axle"
        limit = self.LIMIT_DATABASE.get(v_type, 49000)

        det = {
            'id': len(self.detections) + 1,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'max_rpm': float(feature_max_rpm),
            'predicted_weight': float(predicted_weight),
            'vehicle_type': v_type,   # 记录车型
            'limit': limit,           # 记录这辆车的具体限重
            'is_overloaded': predicted_weight > limit
        }
        self.detections.append(det)
        
        status = "!!! 超载 !!!" if det['is_overloaded'] else "正常"
        print(f"   [检测 Car#{det['id']}] 车型:{v_type} | 限重:{limit/1000}t | 预测:{predicted_weight/1000:.1f}t -> {status}")

    def plot_results(self, save_path=None, sampling_rate=100):
        if len(self.history) == 0: return
        try: plt.style.use('bmh') 
        except: pass
            
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])

        # 上图：波形
        ax1 = plt.subplot(gs[0])
        t = np.arange(len(self.history)) / sampling_rate
        ax1.plot(t, self.history, color='#34495e', linewidth=1.5, label='Encoder Signal')
        ax1.axhline(y=self.threshold, color='gray', linestyle='--', alpha=0.5)

        for d in self.detections:
            t_mid = (d['start_idx'] + d['end_idx']) / 2 / sampling_rate
            color = '#e74c3c' if d['is_overloaded'] else '#2ecc71'
            ax1.axvspan(d['start_idx']/sampling_rate, d['end_idx']/sampling_rate, color=color, alpha=0.15)
            # 标注车型和重量
            ax1.text(t_mid, d['max_rpm'] + 50, f"{d['vehicle_type']}\n{d['predicted_weight']/1000:.1f}t", 
                     ha='center', va='bottom', fontsize=9, fontweight='bold', color=color)

        ax1.set_title('Multi-Sensor Fusion Data Stream (Encoder + Camera Simulation)', fontsize=15, fontweight='bold')
        ax1.set_ylabel('RPM', fontsize=12)
        ax1.legend(loc='upper right')
        
        # 下图：动态限重展示
        ax2 = plt.subplot(gs[1])
        if len(self.detections) > 0:
            ids = [f"#{d['id']}\n({d['vehicle_type']})" for d in self.detections] # X轴显示车型
            weights = [d['predicted_weight'] for d in self.detections]
            limits = [d['limit'] for d in self.detections]
            colors = ['#e74c3c' if d['is_overloaded'] else '#2ecc71' for d in self.detections]
            
            bars = ax2.bar(ids, weights, color=colors, alpha=0.85, width=0.5)
            
            # [核心] 绘制动态的红色限重线 (不再是一条直线，而是每辆车一条短线)
            for i, limit in enumerate(limits):
                # 在每个柱子上画横线表示该车的限重
                ax2.hlines(y=limit, xmin=i-0.3, xmax=i+0.3, colors='#c0392b', linewidth=2.5, linestyles='-')
                ax2.text(i, limit + 1000, f"Limit: {limit/1000}t", ha='center', va='bottom', fontsize=8, color='#c0392b', fontweight='bold')

            for bar, w, d in zip(bars, weights, self.detections):
                height = bar.get_height()
                status = "OVER" if d['is_overloaded'] else "OK"
                ax2.text(bar.get_x() + bar.get_width()/2., height/2,
                         f'{w/1000:.1f} t', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
        
        ax2.set_title('Dynamic Threshold Enforcement Results', fontsize=15, fontweight='bold')
        ax2.set_ylabel('Weight (kg)', fontsize=12)
        ax2.set_ylim(0, 100000)

        plt.tight_layout()
        if save_path: plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

# ==========================================
# 模拟数据生成：可以同时生成波形 + 车型标签
# ==========================================
if __name__ == "__main__":
    system = OverloadDetectionSystem()
    np.random.seed(42)
    
    def generate_car_pass(peak_rpm, duration_points):
        ramp = duration_points // 3
        plateau = duration_points - 2*ramp
        signal = np.concatenate([
            np.linspace(0, peak_rpm, ramp),
            np.full(plateau, peak_rpm) + np.random.normal(0, peak_rpm*0.05, plateau),
            np.linspace(peak_rpm, 0, ramp)
        ])
        return np.abs(signal)

    # === 精心设计的演示剧本 ===
    
    # 场景1: 2轴小货车 (小车，限重18吨)。测量值25吨。 -> 应判定：超载 (红)
    # 虽然25吨 < 49吨，但对于2轴车来说是超载的！
    car1_signal = generate_car_pass(1500, 30) 
    car1_type = "2-Axle" 
    
    # 场景2: 6轴大货车 (大车，限重49吨)。测量值25吨。 -> 应判定：正常 (绿)
    # 同样的转速/重量，对于大车来说是完全正常的。
    car2_signal = generate_car_pass(1500, 45) # 稍微长一点
    car2_type = "6-Axle"
    
    # 场景3: 6轴百吨王 (大车，限重49吨)。测量值70吨。 -> 应判定：严重超载 (红)
    car3_signal = generate_car_pass(4500, 60)
    car3_type = "6-Axle"

    # 场景4: 4轴货车 (中车，限重31吨)。测量值28吨。 -> 应判定：正常 (绿)
    car4_signal = generate_car_pass(1700, 40)
    car4_type = "4-Axle"

    # 组合推流
    gap = np.zeros(50)
    
    # 我们需要把"波形数据"和"车型标签"对应起来
    # 这里用一个简单的逻辑：在波形开始的时候，告诉系统现在的车型
    
    # 构造完整的数据流
    full_stream = np.concatenate([np.zeros(20), car1_signal, gap, car2_signal, gap, car3_signal, gap, car4_signal, np.zeros(100)])
    full_stream += np.abs(np.random.normal(0, 5, len(full_stream))) # 噪声

    # 构造车型时间表 (简单映射：哪段时间对应哪辆车)
    # 我们知道生成顺序，所以在循环里手动切换
    # 这里的逻辑是为了模拟：摄像头在车来的时候发了个信号
    
    print("\n=== 系统启动: 动态阈值与多传感器融合模式 ===\n")
    
    # 指针辅助
    ptr = 0
    current_type_input = None
    
    for i, data in enumerate(full_stream):
        # 简单的时序控制，模拟摄像头同步
        # Car 1 roughly at index 20
        if i == 20: current_type_input = car1_type
        # Car 2 roughly at index 20+30+50 = 100
        elif i == 100: current_type_input = car2_type
        # Car 3 roughly at index 100+45+50 = 195
        elif i == 195: current_type_input = car3_type
        # Car 4 
        elif i == 305: current_type_input = car4_type
        
        # 传入数据和车型
        system.process_realtime_stream(data, 60.0, simulated_vehicle_type=current_type_input)

    output_img = os.path.join(os.path.dirname(__file__), 'dynamic_threshold_demo.png')
    system.plot_results(save_path=output_img)