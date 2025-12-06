import ezdxf
from ezdxf.enums import TextEntityAlignment

def generate_dxf():
    # 1. 创建 DXF
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 2. 图层定义 (红/黄/绿/青/白)
    colors = {'WALL':7, 'COL':2, 'RACK':1, 'CONV':3, 'EQP':4, 'TEXT':7, 'ZONE':6}
    for k, v in colors.items():
        if k not in doc.layers: doc.layers.add(k, color=v)

    # 3. 基础尺寸
    W, H = 24000, 65000
    
    # 绘制围墙 (Wall)
    msp.add_lwpolyline([(0,0), (W,0), (W,H), (0,H), (0,0)], close=True, dxfattribs={'layer':'WALL'})

    # 绘制右下角充电房 (Battery Room - 避让区)
    # 假设尺寸 10m x 12m
    msp.add_lwpolyline([(14000,0), (W,0), (W,12000), (14000,12000), (14000,0)], 
                       close=True, dxfattribs={'layer':'ZONE'})
    msp.add_text("BATTERY ROOM (NO-GO)", dxfattribs={'layer':'TEXT', 'height':400}).set_placement((19000, 6000), align=TextEntityAlignment.MIDDLE_CENTER)

    # 4. 绘制柱子 (单排中轴 X=12000)
    col_y_list = range(10000, 60000, 9000)
    for y in col_y_list:
        msp.add_lwpolyline([(11750, y-250), (12250, y-250), (12250, y+250), (11750, y+250), (11750, y-250)], close=True, dxfattribs={'layer':'COL'})

    # 5. 存储区 (4巷道，避开中间柱子)
    aisles = [4500, 8500, 15500, 19500] # 左右各两条
    for x in aisles:
        # 轨道
        msp.add_line((x, 22000), (x, 63000), dxfattribs={'layer':'RACK', 'linetype':'DASHED'})
        # 货架
        msp.add_lwpolyline([(x-1600,22000), (x-600,22000), (x-600,63000), (x-1600,63000)], close=True, dxfattribs={'layer':'RACK'})
        msp.add_lwpolyline([(x+600,22000), (x+1600,22000), (x+1600,63000), (x+600,63000)], close=True, dxfattribs={'layer':'RACK'})
        # 提升机
        msp.add_lwpolyline([(x-800, 20500), (x+800, 20500), (x+800, 22000), (x-800, 22000)], close=True, dxfattribs={'layer':'EQP'})

    # 6. 输送线 (避开充电房，向北偏移至 Y=19000)
    msp.add_lwpolyline([(1000, 19000), (23000, 19000), (23000, 20000), (1000, 20000)], close=True, dxfattribs={'layer':'CONV'})
    # 连接支线
    for x in aisles:
        msp.add_line((x, 20000), (x, 20500), dxfattribs={'layer':'CONV'})

    # 7. 工作站 (集中在左下角)
    
    # 收货 (Receiving) - 对应月台 1-2
    msp.add_lwpolyline([(1500, 3000), (5500, 3000), (5500, 6000), (1500, 6000)], close=True, dxfattribs={'layer':'EQP'})
    msp.add_text("RECEIVING", dxfattribs={'layer':'TEXT', 'height':400}).set_placement((3500, 4500), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((3500, 6000), (3500, 19000), dxfattribs={'layer':'CONV'}) # 连通 Loop

    # 打包 (Packing) - 对应月台 3-4
    msp.add_lwpolyline([(7500, 3000), (11500, 3000), (11500, 6000), (7500, 6000)], close=True, dxfattribs={'layer':'EQP'})
    msp.add_text("PACKING", dxfattribs={'layer':'TEXT', 'height':400}).set_placement((9500, 4500), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((9500, 6000), (9500, 19000), dxfattribs={'layer':'CONV'}) # 连通 Loop

    # 拣选 (Picking) - 中间缓冲区
    msp.add_lwpolyline([(4000, 13000), (8000, 13000), (8000, 16000), (4000, 16000)], close=True, dxfattribs={'layer':'EQP'})
    msp.add_text("PICKING", dxfattribs={'layer':'TEXT', 'height':400}).set_placement((6000, 14500), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((6000, 16000), (6000, 19000), dxfattribs={'layer':'CONV'})

    doc.saveas("Warehouse_Design_Final.dxf")
    print("文件已生成: Warehouse_Design_Final.dxf")

if __name__ == "__main__":
    generate_dxf()