# To run this script, install python-pptx: pip install python-pptx
# Then, execute: python this_script.py
# It will generate output.pptx in the current directory.

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

prs = Presentation()

# Helper function to add a title to a slide
def add_title(slide, title_text):
    title = slide.shapes.title
    title.text = title_text
    title.text_frame.paragraphs[0].font.size = Pt(32)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# Helper function to add a text box with bullets
def add_text_box(slide, left, top, width, height, title, bullets, is_bullet=True):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    p = tf.add_paragraph()
    p.text = title
    p.font.size = Pt(18)
    p.font.bold = True
    for bullet in bullets:
        p = tf.add_paragraph()
        if is_bullet:
            p.text = bullet
        else:
            p.text = bullet
        p.font.size = Pt(14)

# Slide 1: 选型背景与核心原则 (Left-Right layout: Left pain points, Right principles)
slide1_layout = prs.slide_layouts[1]  # Title and Content
slide1 = prs.slides.add_slide(slide1_layout)
add_title(slide1, "选型背景与核心原则")

# Left: 当前痛点
pain_points = [
    "多点分散、规模偏小\n各快递企业在平安、万德、崮云湖等地设点，资源难以整合",
    "功能单一、自动化水平低\n普遍依赖人工分拣，效率受限，错误率高",
    "仓储资源碎片化\n配送线路重叠，末端派送成本高、时效差"
]
add_text_box(slide1, 0.5, 2, 6, 4, "当前痛点", pain_points)

# Right: 选型核心原则
principles = [
    "✅ 标准化：统一设备规格，支撑未来区域协同",
    "✅ 柔性化：灵活应对电商大促等业务波动",
    "✅ 高性价比：初期投入可控，长期运营成本低",
    "✅ 人机协同友好：降低操作门槛，提升作业安全性与效率"
]
add_text_box(slide1, 6.5, 2, 6, 4, "选型核心原则", principles)

# Slide 2: 叉车设备选型建议 (Two columns)
slide2_layout = prs.slide_layouts[1]
slide2 = prs.slides.add_slide(slide2_layout)
add_title(slide2, "叉车设备选型建议")

# Core demands (top)
core_demands = [
    "适应中小型分拨中心有限作业空间",
    "支持高频次、短距离搬运任务",
    "降低人工劳动强度，提升装卸效率"
]
add_text_box(slide2, 0.5, 1.5, 12, 1.5, "核心需求", core_demands)

# Recommendations (bottom, two columns)
add_text_box(slide2, 0.5, 3.5, 6, 3, "推荐方案\n🔹 主力设备：电动托盘搬运车（地牛）", [
    "成本低、操作灵活、维护简便",
    "适用于分拨中心内部平面货物转运，替代人工手推"
])

add_text_box(slide2, 6.5, 3.5, 6, 3, "🔹 辅助设备：前移式叉车（窄巷道型）", [
    "可在1.7–2米窄通道内作业",
    "支持4–10米高位货架存取，显著提升垂直空间利用率"
])

# Slide 3: 托盘设备选型建议 (Center focus)
slide3_layout = prs.slide_layouts[1]
slide3 = prs.slides.add_slide(slide3_layout)
add_title(slide3, "托盘设备选型建议")

# Core demands
core_demands3 = [
    "高频使用下的高耐用性与低维护成本",
    "满足高校、电商园对卫生与安全的要求",
    "兼容未来自动化设备（如AGV、输送线）"
]
add_text_box(slide3, 0.5, 1.5, 12, 1.5, "核心需求", core_demands3)

# Recommendation
recommendation3 = [
    "耐用免维护：抗摔、防潮、耐腐蚀，全生命周期成本低",
    "卫生安全：表面光滑易清洁，无木屑、虫害风险，符合高标准仓储环境",
    "利于协同：标准化尺寸，便于在各分拨点间流转，为区域仓配一体化及无人机配送等新场景预留接口"
]
add_text_box(slide3, 0.5, 3.5, 12, 3, "推荐方案\n🔸 首选：1200×1000mm 标准塑料托盘（HDPE/PP材质）", recommendation3)

# Note: Add a central image manually for 1200×1000mm pallet diagram

# Slide 4: 货架系统选型建议 (Top image, bottom text)
slide4_layout = prs.slide_layouts[1]
slide4 = prs.slides.add_slide(slide4_layout)
add_title(slide4, "货架系统选型建议")

# Core demands
core_demands4 = [
    "在小面积仓库内最大化存储密度",
    "模块化设计，便于未来扩展或整合",
    "支持快递“快进快出”的高频作业模式"
]
add_text_box(slide4, 0.5, 1.5, 12, 1.5, "核心需求", core_demands4)

# Recommendations
add_text_box(slide4, 0.5, 3.5, 6, 3, "推荐方案\n🔷 主力货架：窄巷道货架（VNA）", [
    "通道宽度仅1.7–2米，比传统货架节省近50%地面空间",
    "配合前移式叉车，实现4–10米高位存取，仓容提升30%以上"
])

add_text_box(slide4, 6.5, 3.5, 6, 3, "🔷 辅助货架：轻型/中型层板货架", [
    "适用于零散小件暂存、分拣区补货",
    "取用灵活，安装便捷，成本低，适合过渡期使用"
])

# Note: Add top diagram manually for narrow aisle rack

# Slide 5: 周转箱选型建议
slide5_layout = prs.slide_layouts[1]
slide5 = prs.slides.add_slide(slide5_layout)
add_title(slide5, "周转箱选型建议")

# Core demands
core_demands5 = [
    "适配电商小批量、多批次订单分拣",
    "易于堆叠、搬运、盘点",
    "有效保护商品，降低货损率"
]
add_text_box(slide5, 0.5, 1.5, 12, 1.5, "核心需求", core_demands5)

# Recommendation
recommendation5 = [
    "行业通用：与1200×1000mm托盘完美匹配，可整齐码放2×2，空间利用率高",
    "坚固耐用：承重≥300kg，抗冲击、防潮，适用于仓内转运及短途配送",
    "功能性强：建议选用带防滑底纹、可稳固堆叠型号；部分箱体可配盖，满足防尘、防盗需求"
]
add_text_box(slide5, 0.5, 3.5, 12, 3, "推荐方案\n🔶 主力周转箱：600×400×340mm 标准塑料周转箱（HDPE/PP材质）", recommendation5)

# Note: Add layout diagram manually for stacked boxes on pallet

# Save the presentation
prs.save('output.pptx')
print("PPTX file created successfully as 'output.pptx'")




from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()

# 添加幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[1])  # 标题和内容布局

# 标题
title = slide.shapes.title
title.text = "4.2.1 物流关系和中国物流关系分析"
title.text_frame.paragraphs[0].font.size = Pt(32)
title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# 上半部分描述文本
left_text = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(4), Inches(1.5))
tf = left_text.text_frame
tf.text = "通过对物流中心作业流程分析\n和功能区的划分，依据预期的物流\n中心物流量，结合实际情况，获得\n物流相互关系。如右图所示。"
tf.paragraphs[0].font.size = Pt(14)

# 上半部分箭头 (使用线条模拟)
arrow = slide.shapes.add_connector(1, Inches(5), Inches(2.75), Inches(6.5), Inches(2.75))  # 直线
arrow.line.color.rgb = RGBColor(0, 0, 255)
arrow.line.width = Pt(2)
# 添加箭头端 (手动或用形状)
arrow_head = slide.shapes.add_shape(3, Inches(6.3), Inches(2.6), Inches(0.3), Inches(0.3))  # 三角形
arrow_head.fill.solid()
arrow_head.fill.fore_color.rgb = RGBColor(0, 0, 255)

# 上半部分表格
table = slide.shapes.add_table(8, 7, Inches(7), Inches(1.5), Inches(5), Inches(3))
# 填充标题和数据 (示例，根据图像调整)
table.cell(0, 0).text = ""
table.cell(0, 1).text = "入库区"
# ... 继续填充其他单元格，如 table.cell(1,1).text = "E" 等
for row in table.rows:
    for cell in row.cells:
        cell.text_frame.paragraphs[0].font.size = Pt(12)
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# 下半部分类似 (调整位置：Inches(1), Inches(5) 等)
# 重复添加文本、箭头、表格

prs.save('relationship_chart.pptx')
print("PPT生成完成！")