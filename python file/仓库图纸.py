import ezdxf
from ezdxf.enums import TextEntityAlignment

def create_visible_warehouse_dxf():
    # 1. 创建文档
    doc = ezdxf.new('R2010')
    
    # 【关键修改1】设置单位为毫米 (4)，并设置绘图范围
    doc.header['$INSUNITS'] = 4  # 4 = Millimeters
    doc.header['$LIMMIN'] = (0, 0)
    doc.header['$LIMMAX'] = (24000, 65000)
    # 设置初始视图中心和高度（辅助 CAD 打开时定位）
    doc.header['$EXTMIN'] = (-5000, -5000, 0)
    doc.header['$EXTMAX'] = (30000, 70000, 0)

    msp = doc.modelspace()

    # 2. 图层设置 (使用最显眼的颜色)
    # 1=红, 2=黄, 3=绿, 4=青, 6=洋红
    layers = [
        ("WALLS", 6),       # 洋红 (非常显眼)
        ("COLUMNS", 2),     # 黄色
        ("RACKS", 3),       # 绿色
        ("CONVEYORS", 4),   # 青色
        ("EQUIPMENT", 1),   # 红色
        ("TEXT", 7),        # 白色
        ("ZONES", 5)        # 蓝色
    ]
    for name, color in layers:
        if name not in doc.layers:
            doc.layers.add(name, color=color)

    # 【关键修改2】定义一个“画粗线”的辅助函数
    # 普通线在远视图下看不见，我们用有宽度的多段线代替
    def add_thick_rect(points, layer, width=200, closed=True):
        # const_width=200 表示线条宽度为200mm，非常粗，容易看见
        msp.add_lwpolyline(points, close=closed, dxfattribs={'layer': layer, 'const_width': width})

    def add_thick_line(p1, p2, layer, width=200):
        msp.add_lwpolyline([p1, p2], dxfattribs={'layer': layer, 'const_width': width})

    W_WIDTH = 24000
    W_LENGTH = 65000
    
    # --- 开始绘图 ---

    # 1. 围墙 (最粗，宽度500mm)
    add_thick_rect([(0, 0), (W_WIDTH, 0), (W_WIDTH, W_LENGTH), (0, W_LENGTH)], "WALLS", width=500)

    # 2. 避让区 (右下角充电房)
    # 使用虚线很难看清，这里直接画实线框
    add_thick_rect([(14000, 0), (W_WIDTH, 0), (W_WIDTH, 12000), (14000, 12000)], "ZONES", width=100)
    msp.add_text("BATTERY ROOM (NO-GO)", dxfattribs={'layer': 'TEXT', 'height': 600}).set_placement((19000, 6000), align=TextEntityAlignment.MIDDLE_CENTER)

    # 3. 柱子 (单排中轴 X=12000)
    col_y_list = range(10000, 60000, 9000)
    for cy in col_y_list:
        # 画一个大大的十字叉
        add_thick_line((11500, cy-500), (12500, cy+500), "COLUMNS", width=150)
        add_thick_line((11500, cy+500), (12500, cy-500), "COLUMNS", width=150)
        # 画柱子轮廓
        add_thick_rect([(11700, cy-300), (12300, cy-300), (12300, cy+300), (11700, cy+300)], "COLUMNS", width=50)

    # 4. 存储区 (4条宽巷道)
    aisle_centers = [4500, 8500, 15500, 19500]
    rack_start_y = 22000
    rack_end_y = 63000
    
    for cx in aisle_centers:
        # 巷道中线 (稍微细一点)
        add_thick_line((cx, rack_start_y), (cx, rack_end_y), "RACKS", width=50)
        
        # 左右货架 (实心框)
        add_thick_rect([(cx-1600, rack_start_y), (cx-600, rack_start_y), (cx-600, rack_end_y), (cx-1600, rack_end_y)], "RACKS", width=100)
        add_thick_rect([(cx+600, rack_start_y), (cx+1600, rack_start_y), (cx+1600, rack_end_y), (cx+600, rack_end_y)], "RACKS", width=100)
        
        # 提升机 (方块)
        add_thick_rect([(cx-800, rack_start_y-1500), (cx+800, rack_start_y-1500), (cx+800, rack_start_y), (cx-800, rack_start_y)], "EQUIPMENT", width=200)
        msp.add_text("LIFT", dxfattribs={'layer': 'TEXT', 'height': 400}).set_placement((cx, rack_start_y-750), align=TextEntityAlignment.MIDDLE_CENTER)

    # 5. 输送线 (宽线条，显眼)
    loop_y = 19000
    # 主环
    add_thick_rect([(1000, loop_y), (23000, loop_y), (23000, loop_y+1200), (1000, loop_y+1200)], "CONVEYORS", width=200)
    
    # 连接支线
    for cx in aisle_centers:
        add_thick_line((cx, loop_y+1200), (cx, rack_start_y-1500), "CONVEYORS", width=150)

    # 6. 工作站 (左下角)
    # 收货区
    add_thick_rect([(1500, 3000), (5500, 3000), (5500, 6000), (1500, 6000)], "EQUIPMENT", width=200)
    msp.add_text("RECEIVING", dxfattribs={'layer': 'TEXT', 'height': 500}).set_placement((3500, 4500), align=TextEntityAlignment.MIDDLE_CENTER)
    add_thick_line((3500, 6000), (3500, loop_y), "CONVEYORS", width=150) # 连线

    # 打包区
    add_thick_rect([(7500, 3000), (11500, 3000), (11500, 6000), (7500, 6000)], "EQUIPMENT", width=200)
    msp.add_text("PACKING", dxfattribs={'layer': 'TEXT', 'height': 500}).set_placement((9500, 4500), align=TextEntityAlignment.MIDDLE_CENTER)
    add_thick_line((9500, 6000), (9500, loop_y), "CONVEYORS", width=150) # 连线

    # 拣选区 (中间)
    add_thick_rect([(4000, 13000), (8000, 13000), (8000, 16000), (4000, 16000)], "EQUIPMENT", width=200)
    msp.add_text("PICKING", dxfattribs={'layer': 'TEXT', 'height': 500}).set_placement((6000, 14500), align=TextEntityAlignment.MIDDLE_CENTER)
    add_thick_line((6000, 16000), (6000, loop_y), "CONVEYORS", width=150)

    # 7. 月台文字
    for i in range(4):
        x = 2000 + i*3000
        msp.add_text(f"DOCK {i+1}", dxfattribs={'layer': 'TEXT', 'height': 500}).set_placement((x+1000, -2000), align=TextEntityAlignment.MIDDLE_CENTER)

    # 保存
    filename = "Warehouse_Visible_V3.dxf"
    doc.saveas(filename)
    print(f"文件已生成: {filename}")
    print("【重要提示】：打开CAD后，请务必双击鼠标中键，或者输入命令 'Z' (空格) -> 'E' (空格) 来查看全图！")

if __name__ == "__main__":
    create_visible_warehouse_dxf()