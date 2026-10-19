from pathlib import Path
import json,collections
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle

root=Path(__file__).resolve().parents[3]
w=Path(__file__).resolve().parent
d=json.loads((w/'recipe_audit.json').read_text())
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/simhei.ttf'))
out=root/'docs/hardware/GPSDO_Skill模块化摆位复核_2026-10-19.pdf'
c=canvas.Canvas(str(out),pagesize=A4)
c.setTitle('GPSDO Skill 模块化摆位复核')
W,H=A4
style=ParagraphStyle('p',fontName='CN',fontSize=9,leading=15,textColor=colors.HexColor('#24344a'))
def paragraph(text,x,y,width=505):
 p=Paragraph(text,style); _,height=p.wrap(width,1000);p.drawOn(c,x,y-height);return y-height-8
def title(text):
 c.setFillColor(colors.HexColor('#174f85'));c.setFont('CN',18);c.drawString(45,H-48,text)
def footer(n):
 c.setStrokeColor(colors.HexColor('#d6dfe8'));c.line(45,39,W-45,39)
 c.setFont('CN',8);c.setFillColor(colors.HexColor('#65758a'));c.drawString(45,26,'GPSDO Rev1.0 | 75 x 75 mm | 四层板 | 2026-10-19');c.drawRightString(W-45,26,str(n))

title('GPSDO Skill 模块化摆位复核')
y=paragraph('本次仅重新摆放元器件。157 个器件全部在正面；保留两个 OCXO 的相对位置及互斥装配、四个安装孔、底边两个 SMA、左侧 Type-C、上方 GNSS，以及 OCXO 上方的 RF 监测模块。',45,H-70)
y=paragraph('方法：kicad-pcb-placement 的几何自检与逐引脚搜索；pcb-plan 提取及核对规划约束。外围件按真实引脚、网络和模块区域归属，未采用通用规划器的错误跨模块归属。位号、数值隐藏。',45,y)
c.drawImage(str(root/'output/pcb/GPSDO_75mm_Skill布局预览.png'),91,170,width=413,height=467,preserveAspectRatio=True,anchor='c')
paragraph('检查：几何自检最大焊盘误差 0.0000 mm；没有额外封装本体碰撞；焊盘 UUID、网络及器件数量一致。走线、过孔、铜区均为 0。DRC 保留原有 16 项：USB 封装内部孔间距 4 项、库一致性 4 项、OCXO 重叠丝印 6 项、USB 板边丝印 2 项。',45,153)
paragraph('重跑提示：relayout.py 从基线生成候选摆位，会替换候选器件位置；apply_candidate.py 才写回工程。后续手工微调后，应先同步配置再重跑。板厂叠层、阻抗、时序和热性能尚需在布线及实物阶段验证。',45,91)
footer(1);c.showPage()

title('关键距离与剩余目标')
y=paragraph('距离均为器件相关焊盘中心到指定芯片引脚中心的直线距离，并非铜线长度。目标值是本项目的摆位优化目标，结合封装尺寸设置，不代表制造商保证值。97 项精确引脚目标中，达到目标的数量由 27 项提升到 79 项。',45,H-70)
b={r['ref']:r for r in d['before']}
selected=['C74','C48','C9','C7','C8','C14','C15','C32','C33']
rows=[['器件 / 用途','原距离 mm','新距离 mm']]
names={'C74':'升压输出电容','C48':'输出驱动 VH 去耦','C9':'TDC VREG 电容','C7':'GNSS 电源去耦','C8':'GNSS 备份电源电容','C14':'MCU VDD 去耦','C15':'MCU VDDA 去耦','C32':'MCU VDD 去耦','C33':'MCU VBAT 去耦'}
for r in d['after']:
 if r['ref'] in selected:rows.append([r['ref']+' / '+names[r['ref']],f"{b[r['ref']]['mm']:.3f}",f"{r['mm']:.3f}"])
def table(rows,y,widths):
 t=Table(rows,colWidths=widths,rowHeights=18)
 t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'CN'),('FONTSIZE',(0,0),(-1,-1),8.5),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f8')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#174f85')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d3dde8')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
 _,h=t.wrap(505,1000);t.drawOn(c,45,y-h);return y-h-12
y=table(rows,y,[285,110,110])
y=paragraph('仍有以下 18 项未严格达到自定义目标。四项仅超出目标不到 0.01 mm，属于搜索网格/保存精度边界；其余主要受封装本体间距及相邻器件限制，保留为后续布线时可微调的项目。',45,y)
rows=[['芯片','外围件','目标 mm','实际 mm']]
for r in d['after']:
 if not r['ok']: rows.append([r['owner'],r['ref'],f"{r['limit']:.2f}",f"{r['mm']:.3f}"])
y=table(rows,y,[125,160,110,110])
paragraph('依据：TI TPS61023 §10.1、TPS7A52 §10.1、TDC7200 §10-11，以及 Renesas ISL55110 Bypassing / Output Damping。完整引脚、目标及前后坐标记录保存在同目录布局工程的 recipe_audit.json 中。',45,y)
footer(2);c.save()
print(out)
