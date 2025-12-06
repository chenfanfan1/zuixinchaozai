import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import xgboost as xgb

# ==========================================
# [核心修改] 配置中文字体，解决方块乱码问题
# ==========================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'PingFang SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示为方块的问题

# ==========================================
# 核心系统类
# ==========================================
class OverloadDetectionSystem:
    def __init__(self, model_filename='xgb_weight_model.json'):
        # 1. 初始化参数
        self.threshold = 50       
        self.min_window_len = 3   
        self.window_buffer = []   
        self.is_recording = False 
        
        # 2. 状态记录
        self.history = []         
        self.detections = []      
        self.current_start_idx = 0
        self.sample_index = 0
        
        # 3. 车型记忆
        self.last_seen_vehicle_type = "6轴车" # 默认值
        self.current_recording_type = None

        # 4. 尝试加载模型
        self.model = xgb.XGBRegressor()
        self.model_loaded = False
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, model_filename)
        
        print(f">> [初始化] 正在尝试加载模型: {model_path}")
        if os.path.exists(model_path):
            try:
                self.model.load_model(model_path)
                self.model_loaded = True
                print(">> [成功] AI模型加载完毕！")
            except Exception as e:
                print(f">> [警告] 模型加载出错 ({e})，将使用物理公式兜底。")
        else:
            print(">> [警告] 未找到模型文件，系统将使用物理公式兜底运行。")

        # 5. [修改] 动态限重标准库 (汉化版 GB 1589)
        self.LIMIT_DATABASE = {
            "2轴车": 18000, 
            "4轴车": 31000, 
            "6轴车": 49000
        }

    def process_realtime_stream(self, sensor_reading, car_speed, vehicle_type=None):
        self.history.append(sensor_reading)

        # 持续更新车型记忆
        if vehicle_type is not None:
            self.last_seen_vehicle_type = vehicle_type

        # STW-OSA 触发逻辑
        if sensor_reading > self.threshold and not self.is_recording:
            self.is_recording = True
            self.window_buffer = []
            self.current_start_idx = self.sample_index
            self.current_recording_type = self.last_seen_vehicle_type
            
        if self.is_recording:
            self.window_buffer.append(sensor_reading)
            if sensor_reading < self.threshold: 
                if len(self.window_buffer) > self.min_window_len:
                    self.is_recording = False
                    end_idx = self.sample_index
                    self._analyze(self.window_buffer, car_speed, self.current_start_idx, end_idx, self.current_recording_type)
                elif len(self.window_buffer) > 200:
                     self.is_recording = False
        
        self.sample_index += 1

    def _analyze(self, data, speed, start_idx, end_idx, v_type):
        arr = np.array(data)
        f_rpm = np.max(arr)
        f_energy = np.sum(arr)
        f_dur = len(arr) * 0.01 

        predicted_weight = 0.0
        
        # AI预测 (带物理公式兜底)
        if self.model_loaded:
            try:
                features = pd.DataFrame([[f_rpm, f_energy, f_dur, speed]], 
                                        columns=['max_rpm', 'energy', 'duration', 'speed'])
                predicted_weight = float(self.model.predict(features)[0])
            except Exception as e:
                predicted_weight = f_rpm * 15.0 + 2000
        else:
            predicted_weight = f_rpm * 15.0 + 2000 
        
        limit = self.LIMIT_DATABASE.get(v_type, 49000)

        self.detections.append({
            'id': len(self.detections)+1,
            'start': start_idx,
            'end': end_idx,
            'max_rpm': f_rpm,
            'weight': predicted_weight,
            'limit': limit,
            'type': v_type,
            'overloaded': predicted_weight > limit
        })
        status_cn = "超载" if predicted_weight > limit else "正常"
        print(f"   -> 车辆离开. 车型:{v_type} 峰值:{f_rpm:.0f} 预测重量:{predicted_weight:.0f}kg ({status_cn})")

    def plot_results(self, save_path=None):
        print(">> [绘图] 正在生成可视化图表...")
        if not self.history: return

        try: plt.style.use('bmh') 
        except: pass
            
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1.5, 1])

        # ==========================================
        # 上图：传感器波形 (汉化)
        # ==========================================
        ax1 = plt.subplot(gs[0])
        t = np.arange(len(self.history)) * 0.01
        
        # [修改] 图例改为中文
        ax1.plot(t, self.history, color='#34495e', lw=1.5, label='编码器转速 (RPM)')
        
        if not self.detections:
            ax1.text(0.5, 0.5, "未检测到车辆数据", transform=ax1.transAxes, ha='center', fontsize=14)
        
        for d in self.detections:
            t_mid = (d['start'] + d['end']) * 0.01 / 2
            color = '#e74c3c' if d['overloaded'] else '#27ae60'
            
            # 区域底色
            ax1.axvspan(d['start']*0.01, d['end']*0.01, color=color, alpha=0.2)
            # 峰值点
            ax1.scatter(t_mid, d['max_rpm'], c=color, s=40, zorder=5)
            # [修改] 标签中文格式化
            label = f"{d['type']}\n{d['weight']/1000:.1f}吨"
            ax1.text(t_mid, d['max_rpm'] + 300, label, ha='center', va='bottom', 
                     fontsize=9, fontweight='bold', color='black',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor=color, boxstyle='round,pad=0.3'))

        # [修改] 标题和坐标轴中文
        ax1.set_title('实时车辆信号监控', fontsize=16, fontweight='bold', pad=15)
        ax1.set_ylabel('转速 (RPM)', fontsize=12)
        ax1.set_xlabel('时间 (秒)', fontsize=12)
        
        max_h = max(self.history) if self.history else 1000
        ax1.set_ylim(-100, max_h * 1.4) 
        ax1.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)

        # ==========================================
        # 下图：动态执法结果 (汉化)
        # ==========================================
        ax2 = plt.subplot(gs[1])
        if self.detections:
            ids = [f"#{d['id']}\n{d['type']}" for d in self.detections]
            weights = [d['weight'] for d in self.detections]
            limits = [d['limit'] for d in self.detections]
            colors = ['#e74c3c' if d['overloaded'] else '#27ae60' for d in self.detections]
            
            bars = ax2.bar(ids, weights, color=colors, alpha=0.85, width=0.5)
            
            # 动态限重线
            for i, limit in enumerate(limits):
                ax2.hlines(y=limit, xmin=i-0.35, xmax=i+0.35, color='#c0392b', lw=2, linestyles='--')
                # [修改] 限重文字中文
                ax2.text(i, limit + 2000, f"限重: {limit/1000}吨", ha='center', va='bottom', 
                         fontsize=10, color='#c0392b', fontweight='bold',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

            # 实际重量文字
            for bar, w, d in zip(bars, weights, self.detections):
                # [修改] 状态改为中文
                status = "超载" if d['overloaded'] else "正常"
                y_text = bar.get_height()/2
                ax2.text(bar.get_x() + bar.get_width()/2, y_text, 
                         f"{w/1000:.1f} 吨\n({status})", 
                         ha='center', va='center', fontsize=11, fontweight='bold', color='white')
        else:
            ax2.text(0.5, 0.5, "暂无执法数据", transform=ax2.transAxes, ha='center')

        # [修改] 标题和坐标轴中文
        ax2.set_title('动态阈值判定结果', fontsize=16, fontweight='bold', pad=15)
        ax2.set_ylabel('预估重量 (kg)', fontsize=12)
        ax2.set_xlabel('检测车辆编号与类型', fontsize=12)
        ax2.set_ylim(0, 100000) 
        
        plt.tight_layout()
        if save_path: 
            plt.savefig(save_path, dpi=150)
            print(f">> [完成] 中文图表已保存至: {save_path}")
        # plt.show() 

# ==========================================
# 模拟数据生成 (调整时间版)
# ==========================================
if __name__ == "__main__":
    system = OverloadDetectionSystem() 
    np.random.seed(42)
    
    def generate_wave(rpm, points):
        ramp = points // 3
        plat = points - 2*ramp
        sig = np.concatenate([
            np.linspace(0, rpm, ramp),
            np.full(plat, rpm) + np.random.normal(0, rpm*0.02, plat),
            np.linspace(rpm, 0, ramp)
        ])
        return np.abs(sig)

    # === 剧本：更真实的时间间隔 ===
    # 采样率 100Hz -> 100个点 = 1秒
    
    # Car 1: 2轴小车 (约25t) -> 红色
    # points=60 (0.6秒的通过时间，模拟车轮压过+机械回弹的全过程)
    wave1 = generate_wave(rpm=1700, points=60)
    type1 = "2轴车"
    
    # Car 2: 6轴大车 (约25t) -> 绿色
    wave2 = generate_wave(rpm=1700, points=80) 
    type2 = "6轴车"
    
    # Car 3: 6轴重车 (约79t) -> 红色
    wave3 = generate_wave(rpm=5000, points=100) # 重车通过时间略长
    type3 = "6轴车"
    
    # Car 4: 4轴车 (约32t) -> 红色
    wave4 = generate_wave(rpm=2000, points=70)
    type4 = "4轴车"

    # [修改点] 调整间隔
    # gap = 350 -> 3.5秒的安全车距
    gap = np.zeros(350)
    
    # 初始等待时间 1秒
    start_wait = np.zeros(100)
    
    stream_segments = [
        (start_wait, None),
        (wave1, type1),
        (gap, None),
        (wave2, type2),
        (gap, None),
        (wave3, type3),
        (gap, None),
        (wave4, type4),
        (np.zeros(200), None) # 结束留白 2秒
    ]
    
    print("\n=== 系统启动: 最终演示模式 (真实时间间隔版) ===\n")
    
    for segment_data, segment_type in stream_segments:
        for val in segment_data:
            # 假设车速 60km/h
            system.process_realtime_stream(val, 60.0, segment_type)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_img = os.path.join(output_dir, 'final_viz_chinese_realtime.png')
    
    system.plot_results(save_path=output_img)
    print("\n=== 运行结束 ===")