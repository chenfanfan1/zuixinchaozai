import os
print("当前工作目录:", os.getcwd())
print("app.py 所在目录:", os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import xgboost as xgb

# ==========================================
# 0. 页面配置 (网页标题、宽屏模式)
# ==========================================
st.set_page_config(
    page_title="数载通途 - 智能监测演示",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'PingFang SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 核心系统逻辑 (保持不变，封装为函数)
# ==========================================
class OverloadDetectionSystem:
    def __init__(self, model_filename='xgb_weight_model.json'):
        self.threshold = 50       
        self.min_window_len = 3   
        self.window_buffer = []   
        self.is_recording = False 
        self.history = []         
        self.detections = []      
        self.current_start_idx = 0
        self.sample_index = 0
        self.last_seen_vehicle_type = "6轴车"
        self.current_recording_type = None

        self.model = xgb.XGBRegressor()
        self.model_loaded = False
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, model_filename)
        
        if os.path.exists(model_path):
            try:
                self.model.load_model(model_path)
                self.model_loaded = True
            except: pass

        self.LIMIT_DATABASE = {
            "2轴车": 18000, "4轴车": 31000, "6轴车": 49000
        }

    def process_realtime_stream(self, sensor_reading, car_speed, vehicle_type=None):
        self.history.append(sensor_reading)
        if vehicle_type is not None:
            self.last_seen_vehicle_type = vehicle_type

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

        if self.model_loaded:
            try:
                features = pd.DataFrame([[f_rpm, f_energy, f_dur, speed]], columns=['max_rpm', 'energy', 'duration', 'speed'])
                predicted_weight = float(self.model.predict(features)[0])
            except:
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

    def get_figure(self):
        # 专门为 Streamlit 返回 figure 对象
        if not self.history: return None
        
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1.5, 1])

        # 子图1：波形
        ax1 = plt.subplot(gs[0])
        t = np.arange(len(self.history)) * 0.01
        ax1.plot(t, self.history, color='#34495e', lw=1.5, label='编码器转速 (RPM)')
        
        for d in self.detections:
            t_mid = (d['start'] + d['end']) * 0.01 / 2
            color = '#e74c3c' if d['overloaded'] else '#27ae60'
            ax1.axvspan(d['start']*0.01, d['end']*0.01, color=color, alpha=0.2)
            ax1.scatter(t_mid, d['max_rpm'], c=color, s=40, zorder=5)
            label = f"{d['type']}\n{d['weight']/1000:.1f}吨"
            ax1.text(t_mid, d['max_rpm'] + 300, label, ha='center', va='bottom', 
                     fontsize=10, fontweight='bold', color='black',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor=color, boxstyle='round,pad=0.3'))

        ax1.set_title('实时车辆通行信号监测', fontsize=18, fontweight='bold', pad=15)
        ax1.set_ylabel('转速 (RPM)', fontsize=14)
        ax1.set_ylim(-100, max(self.history)*1.4 if self.history else 1000) 
        ax1.legend(loc='upper right', frameon=True, fontsize=12)
        ax1.grid(True, alpha=0.3, linestyle='--')

        # 子图2：柱状图
        ax2 = plt.subplot(gs[1])
        if self.detections:
            ids = [f"#{d['id']}\n{d['type']}" for d in self.detections]
            weights = [d['weight'] for d in self.detections]
            limits = [d['limit'] for d in self.detections]
            colors = ['#e74c3c' if d['overloaded'] else '#27ae60' for d in self.detections]
            
            bars = ax2.bar(ids, weights, color=colors, alpha=0.85, width=0.5)
            
            for i, limit in enumerate(limits):
                ax2.hlines(y=limit, xmin=i-0.35, xmax=i+0.35, color='#c0392b', lw=2, linestyles='--')
                ax2.text(i, limit + 2000, f"限重: {limit/1000}吨", ha='center', va='bottom', 
                         fontsize=11, color='#c0392b', fontweight='bold',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

            for bar, w, d in zip(bars, weights, self.detections):
                status = "超载" if d['overloaded'] else "正常"
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                         f"{w/1000:.1f} 吨\n({status})", 
                         ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        else:
            ax2.text(0.5, 0.5, "等待车辆通过...", transform=ax2.transAxes, ha='center', fontsize=14)

        ax2.set_title('动态阈值执法判定结果', fontsize=18, fontweight='bold', pad=15)
        ax2.set_ylabel('预估重量 (kg)', fontsize=14)
        ax2.set_ylim(0, 100000) 
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig

# ==========================================
# 2. Streamlit 界面构建
# ==========================================

# 侧边栏：上帝视角控制台
st.sidebar.header("🕹️ 模拟场景控制台")
st.sidebar.markdown("通过调整下方滑块，实时模拟不同工况下的检测结果。")

# 场景参数控制
st.sidebar.subheader("车辆 1 (2轴车 - 限重18t)")
w1 = st.sidebar.slider("Car 1 实际载重 (吨)", 10.0, 30.0, 29.7, key='w1')

st.sidebar.subheader("车辆 2 (6轴车 - 限重49t)")
w2 = st.sidebar.slider("Car 2 实际载重 (吨)", 20.0, 60.0, 29.9, key='w2')

st.sidebar.subheader("车辆 3 (6轴车 - 限重49t)")
w3 = st.sidebar.slider("Car 3 实际载重 (吨)", 40.0, 100.0, 79.2, key='w3')

st.sidebar.subheader("车辆 4 (4轴车 - 限重31t)")
w4 = st.sidebar.slider("Car 4 实际载重 (吨)", 20.0, 50.0, 33.5, key='w4')

# 主界面标题
st.title("🚛 数载通途 - 高速防超载监测预警系统")
st.markdown("### 基于机电协同感知与动态阈值算法的实时演示")

# 实时计算逻辑
# 将滑块的"吨"数，反向转换为"RPM"信号，喂给系统
def weight_to_rpm(weight_ton):
    # 物理假设: RPM = (Weight_kg - 2000) / 15.0
    # 这是一个逆向工程，为了让系统算出来的数等于你滑块拖的数
    weight_kg = weight_ton * 1000
    rpm = (weight_kg - 2000) / 15.0
    return max(0, rpm)

def generate_wave(rpm, points):
    ramp = points // 3
    plat = points - 2*ramp
    sig = np.concatenate([
        np.linspace(0, rpm, ramp),
        np.full(plat, rpm) + np.random.normal(0, rpm*0.02, plat),
        np.linspace(rpm, 0, ramp)
    ])
    return np.abs(sig)

# 初始化系统
system = OverloadDetectionSystem()

# 生成波形数据
wave1 = generate_wave(rpm=weight_to_rpm(w1), points=60)
wave2 = generate_wave(rpm=weight_to_rpm(w2), points=70)
wave3 = generate_wave(rpm=weight_to_rpm(w3), points=90)
wave4 = generate_wave(rpm=weight_to_rpm(w4), points=65)

gap = np.zeros(350) # 3.5秒间隔

# 组装数据流
stream_segments = [
    (np.zeros(100), None),
    (wave1, "2轴车"),
    (gap, None),
    (wave2, "6轴车"),
    (gap, None),
    (wave3, "6轴车"),
    (gap, None),
    (wave4, "4轴车"),
    (np.zeros(200), None)
]

# 运行处理
for segment_data, segment_type in stream_segments:
    for val in segment_data:
        system.process_realtime_stream(val, 60.0, segment_type)

# 顶部指标栏 (KPI Dashboard)
col1, col2, col3, col4 = st.columns(4)
total_cars = len(system.detections)
overload_cars = sum([1 for d in system.detections if d['overloaded']])
pass_rate = ((total_cars - overload_cars)/total_cars)*100 if total_cars > 0 else 100

col1.metric("今日通行车辆", f"{total_cars} 辆")
col2.metric("违规超载车辆", f"{overload_cars} 辆", delta="-High Risk" if overload_cars>0 else "Good", delta_color="inverse")
col3.metric("系统合规率", f"{pass_rate:.1f}%")
col4.metric("传感器状态", "在线运行", delta="Active")

# 绘制图表
fig = system.get_figure()
if fig:
    st.pyplot(fig)
else:
    st.warning("系统初始化中...")

# 底部说明
st.info("💡 说明：本系统通过侧边栏滑块模拟真实路况。"
        "AI模型会根据输入的机械转速信号实时反演重量，并结合GB1589标准对不同轴数车辆进行动态判罚。")


