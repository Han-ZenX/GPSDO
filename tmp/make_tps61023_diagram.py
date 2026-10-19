from pathlib import Path
import html, math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor as HexColor
from reportlab.lib.units import mm
out=Path(r'G:/C++/GPSDO-master/output/pdf');out.mkdir(exist_ok=True,parents=True)
name='TPS61023_3V3转5V2_STM32控制接线图'
pdfmetrics.registerFont(TTFont('CN',r'C:/Windows/Fonts/simhei.ttf'))
c=canvas.Canvas(str(out/(name+'.pdf')),pagesize=(297*mm,210*mm));c.setTitle(name);c.setAuthor('GPSDO project')
ink='#203448';green='#137B62';blue='#1468A0';red='#B34839';gray='#637487'
class P:
 def __init__(self,n,title):
  self.n=n;self.s=['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><rect width="297" height="210" fill="white"/>']
  self.t(12,14,title,5.4);self.t(12,22,'GPSDO / 保留 ISL55110 / 3.3 V 输入 / STM32 软件使能 / 接线设计图',3,gray);self.l(12,27,285,27,gray,.25)
 def t(self,x,y,t,z=3,col=ink,a='start'):
  c.setFillColor(HexColor(col));c.setFont('CN',z*mm)
  f=c.drawCentredString if a=='middle' else c.drawRightString if a=='end' else c.drawString
  f(x*mm,(210-y)*mm,t)
  self.s.append(f'<text x="{x}" y="{y}" font-size="{z}" font-family="SimHei,Microsoft YaHei,sans-serif" fill="{col}" text-anchor="{a}">{html.escape(t)}</text>')
 def l(self,x,y,u,v,col=green,w=.45):
  c.setStrokeColor(HexColor(col));c.setLineWidth(w*mm);c.line(x*mm,(210-y)*mm,u*mm,(210-v)*mm)
  self.s.append(f'<line x1="{x}" y1="{y}" x2="{u}" y2="{v}" stroke="{col}" stroke-width="{w}"/>')
 def rect(self,x,y,w,h,fill='white',stroke=ink):
  c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(.35*mm);c.rect(x*mm,(210-y-h)*mm,w*mm,h*mm,fill=1,stroke=1)
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width=".35"/>')
 def dot(self,x,y):
  c.setFillColor(HexColor(green));c.circle(x*mm,(210-y)*mm,.65*mm,fill=1,stroke=0);self.s.append(f'<circle cx="{x}" cy="{y}" r=".65" fill="{green}"/>')
 def g(self,x,y):
  self.l(x,y,x,y+2)
  for j,w in enumerate([5,3,1]):self.l(x-w/2,y+2+j,x+w/2,y+2+j)
 def cap(self,x,y,ref,val):
  self.l(x,y,x,y+5);self.l(x-3,y+5,x+3,y+5,ink,.6);self.l(x-3,y+7,x+3,y+7,ink,.6);self.l(x,y+7,x,y+12);self.g(x,y+12);self.t(x+4,y+3,ref,2.7);self.t(x+4,y+8,val,2.5)
 def rv(self,x,y,ref,val):
  self.rect(x-1.5,y,3,12);self.t(x+4,y+4,ref,2.7);self.t(x+4,y+9,val,2.7)
 def rh(self,x,y,ref,val):
  self.rect(x,y-2,10,4);self.t(x+5,y-4.5,ref,2.7,a='middle');self.t(x+5,y+6,val,2.7,a='middle')
 def done(self):
  self.l(12,197,285,197,gray,.25);self.t(12,204,'2026-10-19 | 示例位号；未修改 KiCad 工程 | 图形及 PDF 电路均为矢量',2.6,gray);self.t(285,204,f'{self.n} / 2',2.8,gray,'end')
  self.s.append('</svg>');(out/(name+f'_{self.n:02}.svg')).write_text('\n'.join(self.s),encoding='utf-8');c.showPage()
p=P(1,'TPS61023DRLR：3.3 V 升压至约 5.2 V')
p.t(15,38,'01 / 升压与使能主电路',3.8,blue)
p.t(165,38,'初步按 5.2 V / 200 mA 负载设计；需样板验证',2.8,gray)
# Main chip and pins
p.rect(100,76,48,60,'#F0F6FA');p.t(124,101,'U_BOOST',3.4,a='middle');p.t(124,107,'TPS61023DRLR',3.3,a='middle')
p.l(92,95,100,95,ink);p.t(96,93,'3',2.7,red,'middle');p.t(103,96,'VIN',3)
p.l(92,120,100,120,ink);p.t(96,118,'2',2.7,red,'middle');p.t(103,121,'EN',3)
p.l(124,68,124,76,ink);p.t(121,73,'5',2.7,red);p.t(124,81,'SW',3,a='middle')
p.l(148,90,156,90,ink);p.t(152,88,'6',2.7,red,'middle');p.t(145,91,'VOUT',3,a='end')
p.l(148,130,156,130,ink);p.t(152,128,'1',2.7,red,'middle');p.t(145,131,'FB',3,a='end')
p.l(124,136,124,145,ink);p.t(121,142,'4',2.7,red);p.t(124,133,'GND',3,a='middle');p.g(124,145)
# input rail and choke, no input-output short
p.t(17,51,'+3.3V',3.5,green);p.l(20,55,88,55)
for x in [30,54,70]:p.dot(x,55)
p.l(30,55,30,65);p.cap(30,65,'C1','10uF / 10V')
p.l(54,55,54,83);p.cap(54,83,'C2','100nF')
p.l(70,55,70,95);p.l(70,95,92,95)
p.t(103,44,'L1  1uH',3.2,a='middle');p.t(103,49,'屏蔽电感',2.6,gray,'middle')
# four semicircular coil arcs
p.l(88,55,92,55)
for j in range(4):
 pts=[(92+j*6+k*.25,55-3*math.sin(math.pi*k/24)) for k in range(25)]
 for a,b in zip(pts,pts[1:]):p.l(*a,*b,ink,.45)
p.l(116,55,124,55);p.l(124,55,124,68);p.t(130,61,'SW：短、紧凑',2.7,gray)
# output
p.l(156,90,277,90);p.t(247,84,'+5V2_DRV',3.7,green);p.t(277,97,'至 ISL55110 VH（10脚）',3,a='end')
for x in [174,199,230]:p.dot(x,90)
p.l(174,90,174,101);p.cap(174,101,'C3','22uF / 10V')
p.l(199,90,199,101);p.cap(199,101,'C4','22uF / 10V')
p.l(230,90,230,103);p.rv(230,103,'R3','77.4k / 0.1%');p.l(230,115,230,130);p.dot(230,130)
p.l(156,130,230,130);p.t(176,127,'FB：远离 SW',2.7,gray)
p.l(230,130,230,140);p.rv(230,140,'R4','10.0k / 0.1%');p.l(230,152,230,158);p.g(230,158)
# EN with pulldown at chip side
p.t(15,112,'STM32 GPIO',3,blue);p.l(15,120,40,120);p.rh(40,120,'R1','1k');p.l(50,120,92,120);p.dot(75,120);p.l(75,120,75,135);p.rv(75,135,'R2','10k');p.l(75,147,75,154);p.g(75,154)
p.t(15,141,'BOOST_EN',3,blue);p.t(15,147,'GPIO 号待分配',2.8,gray);p.t(15,153,'复位默认关闭',2.8,gray)
p.rect(14,172,269,18,'#EFF5F8','#C3D4DF')
p.t(18,179,'VOUT = 0.595 × (1 + 77.4k / 10k) = 5.2003 V（PWM 典型值）',3.1)
p.t(18,185,'+5V2_DRV 只供驱动支路；不可与原 +5V 并接。芯片内部同步整流，无需外接肖特基二极管。',2.8,red)
p.done()
p=P(2,'负载接法、元件规格与 STM32 启动流程')
p.t(15,37,'02 / ISL55110 供电局部图',3.8,blue)
# Compact supply fragment
p.rect(198,57,73,54,'#F0F6FA');p.t(234,66,'ISL55110IRZ-T',3.5,a='middle')
p.t(15,48,'+3.3V（直接供电）',3.2,green);p.l(15,53,190,53);p.l(190,53,190,76);p.l(190,76,198,76);p.t(201,77,'1  VDD',3)
p.l(44,53,44,58);p.dot(44,53);p.cap(44,58,'C5','100nF');p.l(93,53,93,58);p.dot(93,53);p.cap(93,58,'C6','4.7uF / 10V')
p.t(15,84,'+5V2_DRV（升压输出）',3.2,green);p.l(15,89,190,89);p.l(190,89,198,89);p.t(201,90,'10  VH',3)
p.l(44,89,44,94);p.dot(44,89);p.cap(44,94,'C7','100nF');p.l(93,89,93,94);p.dot(93,89);p.cap(93,94,'C8','4.7uF / 10V')
p.t(234,104,'11 GND / 17 EP',3,a='middle');p.l(234,111,234,116);p.g(234,116)
p.t(134,100,'C5、C7 紧贴对应供电脚',2.7,gray);p.t(134,106,'两条电源仅共地，不互连',2.7,red)
p.t(15,123,'03 / 外围选型与布局',3.7,blue)
rows=[
('L1','1uH，屏蔽型；初选 Isat ≥ 5A、Irms ≥ 1.5A；按启动/故障电流复核'),
('C1 / C2','10uF：0805 X5R/X7R，3.3V 下有效 ≥ 4.7uF；100nF：0402'),
('C3 / C4','各 22uF：0805/1206 X5R/X7R；5.2V 下合计有效容量 ≥ 10uF'),
('R1 / R2 / R3 / R4','0402；R3、R4 用 0.1%。反馈从输出电容正端安静取样'),
]
for i,(a,b) in enumerate(rows):
 y=128+i*8;p.rect(15,y,267,8,'#F2F6F8' if i%2==0 else 'white','#D3DDE4');p.t(18,y+5.5,a,2.6);p.t(66,y+5.5,b,2.65)
p.t(15,169,'04 / 控制与验证',3.7,blue)
p.t(15,176,'启动：GPIO 先置低 → 初始化 → 3.3V 稳定后延时（初选 20ms）→ EN 拉高 → 确认 VH 稳定。',2.8)
p.t(15,182,'欠压/重启：启用合适 BOR；EN 关断不会主动放空输出电容，快速重启需检查 VH 残压与时序。',2.8)
p.t(15,188,'布线：C3/C4 紧靠 VOUT/GND，缩小高频回路；电感和 SW 远离 TDC、GNSS 与调谐电压。',2.8)
p.done();c.save()
# Companion notes with traceable calculations and source links
notes='''# TPS61023 3.3V 转 5.2V 接线说明\n\n此为矢量接线设计图，未修改 KiCad；位号为示例。保留 ISL55110，STM32 控制升压 EN。\n\n- 官方引脚：1 FB，2 EN，3 VIN，4 GND，5 SW，6 VOUT。1uH 电感接 3.3V 与 SW 之间。\n- R3=77.4k、R4=10.0k，均0.1%；Vout=0.595*(1+77.4/10)=5.2003V。\n- 仅计 PWM 基准0.580～0.610V和电阻独立0.1%极限：输出约5.060～5.341V；未计纹波、负载瞬态、走线压降。PFM需另测。不能把5.2V作为精确恒定值。\n- 暂按200mA负载规划：效率90%时输入约350mA；既有3.3V LDO损耗额外约(5-3.3)*0.35=0.595W。需核算既有负载与温升。\n- L1初选屏蔽1uH、Isat>=5A、Irms>=1.5A，不等于限定输出电流；启动和保护状态需复核。\n- C1=10uF/10V，0805；C3/C4各22uF/10V，0805或1206；按具体料号的DC偏压曲线核实有效容量。\n- EN串1k、对地10k，普通空闲GPIO推挽控制。GPIO编号尚未分配，不能声称固件已实现。\n- MCU启动后延时20ms只是设计初值，不是ISL55110规定间隔。上电时先VDD后VH；可等VH实测稳定后开始输出。\n- 输出没有主动放电：若需可预测重启，预留额外放电电阻/受控放电电路，并结合BOR、复位时序及输出电容实测决定。\n- 取地使用连续地平面，不割裂回流。输入与输出去耦靠近芯片，特别缩小VOUT/输出电容/GND高频回路。\n- 实测至少覆盖冷启动、快速重启、双电源切换、负载阶跃，以及VH最低值/过冲/纹波。\n\n资料：TI TPS61023 SLVSF14B，第3页引脚、第5页电气参数、第12～15页应用、第18页布局。\nhttps://www.ti.com/lit/ds/symlink/tps61023.pdf\nISL55110 FN6228 Rev9.0 第14页要求 Apply VDD, then VH.\nhttps://www.renesas.com/en/document/dst/isl55110-isl55111-datasheet\n'''
(out/(name+'.md')).write_text(notes,encoding='utf-8')
# Check resistor tolerance calculation
vmin=.580*(1+77.4*.999/(10*1.001));vmax=.610*(1+77.4*1.001/(10*.999))
print('Vout bounds',vmin,vmax)
print(out/(name+'.pdf'))
import pypdfium2 as pdfium
r=pdfium.PdfDocument(str(out/(name+'.pdf')))
for i in range(len(r)):
 r[i].render(scale=1.5).to_pil().save(str(out/(name+f'_preview_{i+1}.png')))

