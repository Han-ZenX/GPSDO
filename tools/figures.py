#!/usr/bin/env python3
"""
md2pdf.py 的配套绘图模块：为硬件文档生成矢量示意图。

在 Markdown 中用 `@fig:名称 图题` 单独一行引用，例如:
    @fig:stackup 图 2　四层板叠层剖面（1.6 mm）

纯 reportlab.graphics 矢量绘制，不依赖外部图片文件。
"""

import math

from reportlab.graphics.shapes import (Circle, Drawing, Group, Line, PolyLine, Polygon,
                                       Rect, String)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

W = 170 * mm  # 与正文同宽

FONT, BOLD = 'NotoSC', 'NotoSC-Bold'
ACCENT = colors.HexColor('#1a5f9c')
DARK = colors.HexColor('#1a1a1a')
GREY = colors.HexColor('#666666')
COPPER = colors.HexColor('#c8801f')
DIEL = colors.HexColor('#d9e6c9')
CORE_C = colors.HexColor('#c3d6ae')
MASK = colors.HexColor('#2f7a4f')
RED = colors.HexColor('#c0392b')
AMBER = colors.HexColor('#d68910')
GREEN = colors.HexColor('#1e8449')

CAP = ParagraphStyle('cap', fontName=FONT, fontSize=8.5, leading=12.5,
                     textColor=GREY, alignment=1, spaceBefore=3, spaceAfter=10)


def _txt(d, x, y, s, size=8, font=FONT, fill=DARK, anchor='start'):
    d.add(String(x, y, s, fontName=font, fontSize=size,
                 fillColor=fill, textAnchor=anchor))


def _box(d, x, y, w, h, fill, stroke=None, sw=0.6, r=None):
    kw = dict(fillColor=fill, strokeColor=stroke or colors.HexColor('#94a7b8'),
              strokeWidth=sw)
    if r:
        kw['rx'] = kw['ry'] = r
    d.add(Rect(x, y, w, h, **kw))


def _arrow(d, x1, y1, x2, y2, color=ACCENT, sw=1.0, head=4):
    """带箭头的直线（仅支持水平/垂直方向的箭头）。"""
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=sw))
    if abs(x2 - x1) < 0.01:                       # 垂直
        s = -head if y2 < y1 else head
        d.add(Polygon([x2, y2, x2 - head * 0.6, y2 - s, x2 + head * 0.6, y2 - s],
                      fillColor=color, strokeColor=color))
    else:                                          # 水平
        s = -head if x2 < x1 else head
        d.add(Polygon([x2, y2, x2 - s, y2 - head * 0.6, x2 - s, y2 + head * 0.6],
                      fillColor=color, strokeColor=color))


# ---------------------------------------------------------------- 图：流程总览

def flow():
    """十阶段流程总览，边框颜色表示返工代价。"""
    d = Drawing(W, 250)
    stages = [
        ('一', '开工前决策', '层数 / 板厂 / 板框', RED),
        ('二', '原理图收尾', '批注 / 封装 / ERC', AMBER),
        ('三', '电路板配置', '叠层 / 规则 / 网络类', RED),
        ('四', '更新 PCB', '从原理图导入', GREEN),
        ('五', '板框与结构', 'Edge.Cuts / 安装孔', AMBER),
        ('六', '布局', '摆放 / 分区 / 锁定', RED),
        ('七', '布线', '优先级 / 阻抗 / 等长', AMBER),
        ('八', '铺铜与回流', '平面 / 缝合过孔', GREEN),
        ('九', '检查', 'DRC / 目视 / 3D', ACCENT),
        ('十', '制造输出', 'Gerber / 钻孔 / BOM', GREEN),
    ]
    bw, bh, gx, gy = 218, 38, 24, 8
    x0, y0 = 4, 250 - bh - 16
    for i, (num, name, sub, col) in enumerate(stages):
        cx = x0 + (i % 2) * (bw + gx)
        cy = y0 - (i // 2) * (bh + gy)
        _box(d, cx, cy, bw, bh, colors.white, col, 1.1, r=4)
        d.add(Rect(cx, cy, 4, bh, fillColor=col, strokeColor=col))
        _txt(d, cx + 12, cy + bh - 15, '阶段' + num, 8.5, BOLD, col)
        _txt(d, cx + 52, cy + bh - 15, name, 9.5, BOLD, DARK)
        _txt(d, cx + 12, cy + 8, sub, 7.5, FONT, GREY)
        if i % 2 == 0:                              # 左 -> 右
            _arrow(d, cx + bw + 3, cy + bh / 2, cx + bw + gx - 3, cy + bh / 2, GREY, .8)
        elif i < len(stages) - 1:                   # 右 -> 下一行左
            _arrow(d, cx + bw / 2, cy - 1, cx + bw / 2, cy - gy + 1, GREY, .8)

    ly = 12
    _txt(d, 4, ly, '返工代价：', 8, BOLD, DARK)
    for i, (c, t) in enumerate(((RED, '极高 / 高'), (AMBER, '高 / 中'),
                                (GREEN, '低'), (ACCENT, '检查环节'))):
        bx = 52 + i * 96
        d.add(Rect(bx, ly - 1, 16, 7, fillColor=colors.white, strokeColor=c, strokeWidth=1.1))
        _txt(d, bx + 21, ly, t, 8, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：叠层剖面

def stackup():
    """四层板 1.6 mm 叠层剖面（嘉立创 JLC04161H-7628）。"""
    d = Drawing(W, 232)
    layers = [
        ('阻焊 / Solder Mask', '0.01 mm', MASK, 7, ''),
        ('F.Cu  (1 oz)', '0.035 mm', COPPER, 11, '信号层：射频、差分时钟'),
        ('Prepreg 7628', '0.2104 mm', DIEL, 26, 'Dk 4.4　← 决定 F.Cu 阻抗'),
        ('In1.Cu  (0.5 oz)', '0.0152 mm', COPPER, 9, 'GND 完整平面（不可分割）'),
        ('Core', '1.065 mm', CORE_C, 52, 'Dk 4.2'),
        ('In2.Cu  (0.5 oz)', '0.0152 mm', COPPER, 9, 'PWR 电源平面'),
        ('Prepreg 7628', '0.2104 mm', DIEL, 26, 'Dk 4.4'),
        ('B.Cu  (1 oz)', '0.035 mm', COPPER, 11, '次信号层'),
        ('阻焊 / Solder Mask', '0.01 mm', MASK, 7, ''),
    ]
    lx, lw = 92, 210
    y = 232 - 26
    for name, th, col, h, note in layers:
        y -= h
        _box(d, lx, y, lw, h, col, colors.HexColor('#7d8f9e'), 0.5)
        _txt(d, lx - 6, y + h / 2 - 3, name, 7.5, FONT, DARK, 'end')
        _txt(d, lx + lw + 8, y + h / 2 - 3, th, 7.5, BOLD, ACCENT)
        if note:
            _txt(d, lx + lw + 62, y + h / 2 - 3, note, 7.5, FONT, GREY)

    top, bot = 232 - 26, y
    d.add(Line(lx - 76, top, lx - 76, bot, strokeColor=ACCENT, strokeWidth=0.8))
    for yy in (top, bot):
        d.add(Line(lx - 80, yy, lx - 72, yy, strokeColor=ACCENT, strokeWidth=0.8))
    _txt(d, lx - 84, (top + bot) / 2 - 3, '1.6 mm', 8, BOLD, ACCENT, 'end')

    # 高亮 F.Cu 与 In1.Cu 之间的关键间距
    ky1 = top - 7 - 11
    ky2 = ky1 - 26
    d.add(Line(lx + lw + 168, ky1, lx + lw + 168, ky2, strokeColor=RED, strokeWidth=0.9))
    for yy in (ky1, ky2):
        d.add(Line(lx + lw + 164, yy, lx + lw + 172, yy, strokeColor=RED, strokeWidth=0.9))
    _txt(d, lx + lw + 176, (ky1 + ky2) / 2 - 3, 'H', 8.5, BOLD, RED)

    _txt(d, 4, 8, '计算阻抗时 H 填这一段（0.2104 mm），不是板厚 1.6 mm', 8, BOLD, RED)
    return d


# ---------------------------------------------------------------- 图：微带线截面

def microstrip():
    """微带线截面与计算器参数对应关系。"""
    d = Drawing(W, 165)
    bx, bw2, by = 60, 300, 46
    d.add(Rect(bx, by, bw2, 42, fillColor=DIEL, strokeColor=colors.HexColor('#7d8f9e')))
    d.add(Rect(bx, by - 10, bw2, 10, fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e')))
    tw, tx = 54, bx + 120
    d.add(Rect(tx, by + 42, tw, 11, fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e')))

    _txt(d, bx - 6, by - 8, 'In1.Cu', 8, BOLD, DARK, 'end')
    _txt(d, bx - 6, by + 18, 'Prepreg', 8, FONT, DARK, 'end')
    _txt(d, bx + bw2 + 8, by - 8, '参考平面（完整 GND）', 8, FONT, GREY)
    _txt(d, tx + tw + 10, by + 45, '走线 (F.Cu)', 8, FONT, GREY)

    # W 标注
    d.add(Line(tx, by + 68, tx + tw, by + 68, strokeColor=ACCENT, strokeWidth=0.9))
    for xx in (tx, tx + tw):
        d.add(Line(xx, by + 64, xx, by + 72, strokeColor=ACCENT, strokeWidth=0.9))
    _txt(d, tx + tw / 2, by + 74, 'W 线宽', 8.5, BOLD, ACCENT, 'middle')
    # H 标注
    hx = bx + 40
    d.add(Line(hx, by, hx, by + 42, strokeColor=RED, strokeWidth=0.9))
    for yy in (by, by + 42):
        d.add(Line(hx - 4, yy, hx + 4, yy, strokeColor=RED, strokeWidth=0.9))
    _txt(d, hx + 8, by + 18, 'H 介质厚度', 8.5, BOLD, RED)
    # T 标注
    d.add(Line(tx + tw + 4, by + 42, tx + tw + 4, by + 53, strokeColor=GREEN, strokeWidth=0.9))
    _txt(d, tx + tw + 8, by + 44, 'T 铜厚', 8, BOLD, GREEN)

    _txt(d, 4, 22, 'KiCad 计算器对应：εr = 介质 Dk　|　H = 介质厚度（非板厚）　|　'
                   'T = 铜厚　|　W = 合成结果', 8, FONT, DARK)
    _txt(d, 4, 8, 'H(top) 保持 1e+20，表示走线上方为空气、无金属盖板', 8, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：布线优先级

def priority():
    """布线优先级阶梯。"""
    d = Drawing(W, 208)
    items = [
        ('1', '去耦电容 → 电源/地引脚', '环路面积最小'),
        ('2', '晶振、时钟源', '最短最直，远离干扰'),
        ('3', '阻抗控制线：射频、差分时钟', '线宽固定，无腾挪余地'),
        ('4', '其他差分对：以太网、USB', '需成对等距'),
        ('5', '敏感模拟信号', '远离数字与开关电源'),
        ('6', '高速数字总线', '需等长、成组'),
        ('7', '普通数字 I/O、LED、按键', '最灵活，随便绕'),
        ('8', '电源走线', '加宽即可，最后填空隙'),
    ]
    bh, gy = 20, 3.5
    y = 208 - 26
    for i, (n, name, why) in enumerate(items):
        y -= bh
        ratio = 1 - i * 0.055
        bw2 = 300 * ratio
        col = RED if i < 4 else (AMBER if i < 6 else GREEN)
        _box(d, 40, y, bw2, bh, colors.white, col, 1.0, r=3)
        d.add(Rect(40, y, 3.5, bh, fillColor=col, strokeColor=col))
        _txt(d, 22, y + 6, n, 10, BOLD, col, 'middle')
        _txt(d, 50, y + 6, name, 8.5, FONT, DARK)
        _txt(d, 352, y + 6, why, 7.5, FONT, GREY)
        y -= gy

    _arrow(d, 12, 208 - 30, 12, y + 14, ACCENT, 1.0)
    _txt(d, 4, 208 - 18, '先', 8, BOLD, ACCENT)
    _txt(d, 4, y + 4, '后', 8, BOLD, ACCENT)
    _txt(d, 40, 8, '越敏感、越难改的越先走；LED 按键这类线多晚布都能绕过去', 8, BOLD, DARK)
    return d


# ---------------------------------------------------------------- 图：回流路径

def refplane():
    """参考平面完整 vs 被割断时的回流路径对比。"""
    d = Drawing(W, 175)
    pw, ph = 218, 88
    for k, (px, title, ok) in enumerate((
            (6, '完整参考平面', True),
            (6 + pw + 24, '平面被走线割断', False))):
        py = 58
        _box(d, px, py, pw, ph, colors.HexColor('#f4f7fa'),
             GREEN if ok else RED, 1.1, r=3)
        # 信号走线（上方）
        sy = py + ph - 22
        d.add(Line(px + 20, sy, px + pw - 20, sy, strokeColor=COPPER, strokeWidth=2.4))
        _txt(d, px + 20, sy + 7, '信号走线 (F.Cu)', 7.5, FONT, GREY)
        # 参考平面（下方）
        gy2 = py + 26
        if ok:
            d.add(Rect(px + 14, gy2, pw - 28, 9, fillColor=COPPER,
                       strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
        else:
            gap = 34
            midx = px + pw / 2
            d.add(Rect(px + 14, gy2, midx - gap / 2 - (px + 14), 9, fillColor=COPPER,
                       strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
            d.add(Rect(midx + gap / 2, gy2, (px + pw - 14) - (midx + gap / 2), 9,
                       fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
            _txt(d, midx, gy2 - 12, '割缝', 7.5, BOLD, RED, 'middle')
        _txt(d, px + 14, gy2 + 14, 'In1.Cu (GND)', 7.5, FONT, GREY)

        # 回流路径
        if ok:
            d.add(PolyLine([px + 60, sy - 4, px + 60, gy2 + 13,
                            px + pw - 60, gy2 + 13, px + pw - 60, sy - 4],
                           strokeColor=GREEN, strokeWidth=1.3,
                           strokeDashArray=[3, 2]))
            _txt(d, px + pw / 2, gy2 + 18, '回流路径短', 7.5, BOLD, GREEN, 'middle')
        else:
            midx = px + pw / 2
            d.add(PolyLine([px + 60, sy - 4, px + 60, gy2 + 13, midx - 20, gy2 + 13,
                            midx - 20, py + 8, midx + 20, py + 8,
                            midx + 20, gy2 + 13, px + pw - 60, gy2 + 13,
                            px + pw - 60, sy - 4],
                           strokeColor=RED, strokeWidth=1.3, strokeDashArray=[3, 2]))
            _txt(d, midx, py + 1, '回流被迫绕行 → 阻抗突变、辐射、串扰', 7.5, BOLD, RED, 'middle')

        _txt(d, px + pw / 2, py + ph + 8, title, 9, BOLD,
             GREEN if ok else RED, 'middle')

    _txt(d, 6, 30, '高频回流电流总是走信号线正下方的最短路径。参考平面上任何割缝都会迫使回流绕行，',
         8, FONT, DARK)
    _txt(d, 6, 17, '同时破坏阻抗连续性并显著增加辐射。这是 In1.Cu 不允许走线的根本原因。',
         8, FONT, DARK)
    return d


# ---------------------------------------------------------------- 图：布局分区

def layout():
    """CORE 底板的布局分区示意。"""
    d = Drawing(W, 215)
    bx, by, bw2, bh2 = 30, 34, 420, 160
    _box(d, bx, by, bw2, bh2, colors.white, DARK, 1.2, r=3)
    _txt(d, bx, by + bh2 + 8, '板框 (Edge.Cuts)', 8, FONT, GREY)

    zones = [
        (bx + 8, by + 8, 130, 144, '#fdeaea', RED, '射频区', 'SMA ×8 输入\n50Ω 控制\n最短路径'),
        (bx + 146, by + 8, 150, 144, '#eaf1f8', ACCENT, '数字区', 'ZYNQ 核心板座\n差分时钟\n高速总线'),
        (bx + 304, by + 78, 108, 74, '#eaf6ee', GREEN, '电源区', '稳压器\n大电容'),
        (bx + 304, by + 8, 108, 62, '#fdf6e6', AMBER, '接口区', 'RJ45 / USB-C'),
    ]
    for zx, zy, zw, zh, fill, col, name, items in zones:
        _box(d, zx, zy, zw, zh, colors.HexColor(fill), col, 0.9, r=3)
        _txt(d, zx + 6, zy + zh - 13, name, 9, BOLD, col)
        for j, ln in enumerate(items.split('\n')):
            _txt(d, zx + 6, zy + zh - 27 - j * 11, ln, 7.5, FONT, GREY)

    # 板边接口标记
    for cy, lbl in ((by + 130, 'SMA'), (by + 100, 'SMA'), (by + 70, 'SMA'), (by + 40, 'SMA')):
        d.add(Rect(bx - 7, cy, 7, 12, fillColor=COPPER, strokeColor=DARK, strokeWidth=0.5))
    _txt(d, bx - 12, by + 12, 'SMA ×8', 7.5, BOLD, DARK, 'end')
    for cx, lbl in ((bx + 330, 'RJ45'), (bx + 386, 'USB-C')):
        d.add(Rect(cx, by - 7, 34, 7, fillColor=COPPER, strokeColor=DARK, strokeWidth=0.5))
        _txt(d, cx + 17, by - 17, lbl, 7.5, BOLD, DARK, 'middle')

    _txt(d, 6, 16, '三条原则：就近（去耦电容贴紧电源脚）　|　分区（模拟/数字/电源/射频分开）　|　'
                   '信号流向（避免来回穿越）', 8, FONT, DARK)
    return d


# ------------------------------------------------------- 图：原理图流程总览

def sch_flow():
    """原理图设计八阶段。"""
    d = Drawing(W, 212)
    stages = [
        ('一', '工程与图纸准备', '新建工程 / 页面设置 / 图框', GREEN),
        ('二', '符号库准备', '标准库 / 自建符号 / 库路径', AMBER),
        ('三', '绘制电路', '放符号 / 连线 / 标签', ACCENT),
        ('四', '层次化拆分', '按功能分图纸 / 层次标签', AMBER),
        ('五', '批注位号', '分配唯一 R1 C2 U3', GREEN),
        ('六', '分配封装', '与实际采购件对应', RED),
        ('七', 'ERC 检查', '引脚冲突 / 未连接 / 电源', RED),
        ('八', '输出', 'BOM / 网表 / 更新 PCB', GREEN),
    ]
    bw, bh, gx, gy = 218, 38, 24, 8
    x0, y0 = 4, 212 - bh - 14
    for i, (num, name, sub, col) in enumerate(stages):
        cx = x0 + (i % 2) * (bw + gx)
        cy = y0 - (i // 2) * (bh + gy)
        _box(d, cx, cy, bw, bh, colors.white, col, 1.1, r=4)
        d.add(Rect(cx, cy, 4, bh, fillColor=col, strokeColor=col))
        _txt(d, cx + 12, cy + bh - 15, '阶段' + num, 8.5, BOLD, col)
        _txt(d, cx + 52, cy + bh - 15, name, 9.5, BOLD, DARK)
        _txt(d, cx + 12, cy + 8, sub, 7.5, FONT, GREY)
        if i % 2 == 0:
            _arrow(d, cx + bw + 3, cy + bh / 2, cx + bw + gx - 3, cy + bh / 2, GREY, .8)
        elif i < len(stages) - 1:
            _arrow(d, cx + bw / 2, cy - 1, cx + bw / 2, cy - gy + 1, GREY, .8)
    _txt(d, 4, 10, '阶段六、七出错会直接导致板子报废或返工，是全流程的两个卡点',
         8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：六种连接方式

def sch_connect():
    """原理图中六种建立连接的方式对比。"""
    d = Drawing(W, 268)
    rows = [
        ('导线 / Wire', 'W', '直接画线相连', '同一图纸内看得见的物理连接'),
        ('结点 / Junction', 'J', '交叉处的实心圆点', '无圆点的交叉线不相连'),
        ('网络标签 / Label', 'L', '同名 = 相连', '仅在本张图纸内生效'),
        ('全局标签 / Global Label', 'Ctrl+L', '同名 = 相连', '跨所有图纸生效'),
        ('层次标签 / Hier. Label', 'H', '对应父图纸的图纸引脚', '子图与父图的接口'),
        ('电源符号 / Power', 'P', '同名 = 自动相连', 'GND、+3V3 等全局连通'),
    ]
    rh = 38
    y = 268 - 24
    for name, key, how, note in rows:
        y -= rh
        _box(d, 4, y, W - 8, rh - 4, colors.HexColor('#f8fafb'),
             colors.HexColor('#d5dee7'), 0.6, r=3)
        _txt(d, 12, y + rh - 18, name, 9, BOLD, ACCENT)
        d.add(Rect(150, y + rh - 22, 34, 13, fillColor=colors.white,
                   strokeColor=ACCENT, strokeWidth=0.8, rx=2, ry=2))
        _txt(d, 167, y + rh - 18, key, 8, BOLD, ACCENT, 'middle')
        _txt(d, 12, y + 8, how, 7.5, FONT, DARK)
        _txt(d, 150, y + 8, note, 7.5, FONT, GREY)

        # 右侧小示意
        gx0, gy0 = 340, y + rh / 2 - 2
        if name.startswith('导线'):
            d.add(Line(gx0, gy0, gx0 + 60, gy0, strokeColor=GREEN, strokeWidth=1.4))
            for xx in (gx0, gx0 + 60):
                d.add(Rect(xx - 3, gy0 - 3, 6, 6, fillColor=DARK, strokeColor=DARK))
        elif name.startswith('结点'):
            d.add(Line(gx0, gy0, gx0 + 60, gy0, strokeColor=GREEN, strokeWidth=1.4))
            d.add(Line(gx0 + 30, gy0 - 14, gx0 + 30, gy0 + 14, strokeColor=GREEN, strokeWidth=1.4))
            d.add(Polygon([gx0 + 30, gy0 + 3.2, gx0 + 33.2, gy0, gx0 + 30, gy0 - 3.2,
                           gx0 + 26.8, gy0], fillColor=DARK, strokeColor=DARK))
        elif name.startswith('网络标签'):
            for k, off in ((0, 0), (1, 76)):
                d.add(Line(gx0 + off, gy0, gx0 + off + 26, gy0,
                           strokeColor=GREEN, strokeWidth=1.4))
                _txt(d, gx0 + off + 28, gy0 - 3, 'SDA', 7.5, BOLD, ACCENT)
            _txt(d, gx0 + 56, gy0 + 8, '=', 9, BOLD, GREY)
        elif name.startswith('全局标签'):
            for off, lbl in ((0, '图纸 A'), (76, '图纸 B')):
                d.add(Rect(gx0 + off, gy0 - 10, 52, 20, fillColor=colors.white,
                           strokeColor=GREY, strokeWidth=0.5, rx=2, ry=2))
                _txt(d, gx0 + off + 26, gy0 - 3, lbl, 7, FONT, GREY, 'middle')
            _arrow(d, gx0 + 54, gy0, gx0 + 74, gy0, ACCENT, 1.0, 3.5)
        elif name.startswith('层次标签'):
            d.add(Rect(gx0, gy0 - 12, 56, 24, fillColor=colors.white,
                       strokeColor=ACCENT, strokeWidth=0.9, rx=2, ry=2))
            _txt(d, gx0 + 28, gy0 - 3, '父图纸', 7, FONT, ACCENT, 'middle')
            d.add(Rect(gx0 + 54, gy0 - 3, 6, 6, fillColor=AMBER, strokeColor=AMBER))
            _arrow(d, gx0 + 62, gy0, gx0 + 84, gy0, AMBER, 1.0, 3.5)
            _txt(d, gx0 + 88, gy0 - 3, '子图', 7, FONT, AMBER)
        else:
            for off in (0, 60):
                d.add(Line(gx0 + off + 12, gy0 + 10, gx0 + off + 12, gy0,
                           strokeColor=GREEN, strokeWidth=1.4))
                d.add(Line(gx0 + off + 4, gy0, gx0 + off + 20, gy0,
                           strokeColor=GREEN, strokeWidth=1.6))
                _txt(d, gx0 + off + 12, gy0 - 11, 'GND', 7, BOLD, ACCENT, 'middle')
            _txt(d, gx0 + 40, gy0 + 2, '=', 9, BOLD, GREY)

    _txt(d, 4, 8, '常见错误：交叉处漏放结点导致该连的没连；用网络标签跨图纸连接（不生效，'
                  '需用全局标签）', 8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：层次化结构

def sch_hierarchy():
    """层次化原理图的父子对应关系。"""
    d = Drawing(W, 226)
    # 顶层
    tx, ty, tw, th = 90, 150, 300, 60
    _box(d, tx, ty, tw, th, colors.HexColor('#eaf1f8'), ACCENT, 1.2, r=4)
    _txt(d, tx + 8, ty + th - 15, '顶层图纸 / Root Sheet', 9, BOLD, ACCENT)
    sheets = [('电源.kicad_sch', tx + 14), ('射频前端.kicad_sch', tx + 108),
              ('接口.kicad_sch', tx + 214)]
    pins = []
    for name, sx in sheets:
        d.add(Rect(sx, ty + 8, 78, 28, fillColor=colors.white,
                   strokeColor=DARK, strokeWidth=0.8))
        _txt(d, sx + 39, ty + 24, '图纸符号', 7, FONT, GREY, 'middle')
        _txt(d, sx + 39, ty + 13, name.replace('.kicad_sch', ''), 7.5, BOLD, DARK, 'middle')
        px, py = sx + 78, ty + 22
        d.add(Rect(px - 3, py - 3, 6, 6, fillColor=AMBER, strokeColor=AMBER))
        pins.append((px, py, sx + 39))
    _txt(d, tx + tw + 8, ty + 22, '图纸引脚', 7.5, BOLD, AMBER)
    _txt(d, tx + tw + 8, ty + 11, 'Sheet Pin', 7, FONT, GREY)

    # 子图
    cy = 44
    for i, (name, sx) in enumerate(sheets):
        cx = 24 + i * 152
        _box(d, cx, cy, 132, 62, colors.HexColor('#fdf6e6'), AMBER, 1.0, r=4)
        _txt(d, cx + 8, cy + 48, name.replace('.kicad_sch', '') + ' 子图', 8, BOLD, AMBER)
        d.add(Rect(cx + 8, cy + 26, 6, 6, fillColor=AMBER, strokeColor=AMBER))
        _txt(d, cx + 20, cy + 26, '层次标签 (H)', 7.5, FONT, DARK)
        _txt(d, cx + 8, cy + 10, '名称必须与图纸引脚一致', 7, FONT, GREY)
        _arrow(d, pins[i][2], ty - 2, cx + 66, cy + 64, ACCENT, 0.8, 3.5)

    _txt(d, 4, 20, '层次标签 (H) 与父图纸上的图纸引脚 **同名即相连**，是子图对外的唯一接口。',
         8, FONT, DARK)
    _txt(d, 4, 8, '快捷键：S 放置图纸　|　Ctrl+H 层次导航　|　Alt+Back 离开图纸　|　'
                  'PgUp / PgDn 翻页', 8, FONT, GREY)
    return d


# ------------------------------------------------------- 图：数据流

def sch_dataflow():
    """符号库 -> 原理图 -> 封装 -> PCB 的数据流。"""
    d = Drawing(W, 168)
    steps = [
        ('符号库', '.kicad_sym', '引脚定义\n电气类型', ACCENT),
        ('原理图', '.kicad_sch', '位号 Reference\n数值 Value\n封装 Footprint', GREEN),
        ('封装库', '.pretty', '焊盘尺寸\n实际外形', AMBER),
        ('PCB', '.kicad_pcb', '焊盘 + 飞线\n网络连接', RED),
    ]
    bw, gx = 104, 34
    x = 8
    y = 62
    for i, (name, ext, items, col) in enumerate(steps):
        _box(d, x, y, bw, 74, colors.white, col, 1.2, r=4)
        d.add(Rect(x, y + 58, bw, 16, fillColor=col, strokeColor=col,
                   rx=4, ry=4))
        _txt(d, x + bw / 2, y + 63, name, 9, BOLD, colors.white, 'middle')
        _txt(d, x + bw / 2, y + 46, ext, 7, FONT, GREY, 'middle')
        for j, ln in enumerate(items.split('\n')):
            _txt(d, x + 8, y + 32 - j * 11, ln, 7.5, FONT, DARK)
        if i < len(steps) - 1:
            _arrow(d, x + bw + 4, y + 37, x + bw + gx - 4, y + 37, ACCENT, 1.2, 4.5)
        x += bw + gx

    _txt(d, 118, 146, '分配封装', 7.5, BOLD, ACCENT)
    _txt(d, 256, 146, '引用', 7.5, BOLD, ACCENT)
    _txt(d, 388, 146, '从原理图更新 PCB', 7.5, BOLD, ACCENT)

    _txt(d, 8, 40, '关键：原理图里的「封装」字段只是一个名字字符串，它必须能在封装库里找到对应项。',
         8, FONT, DARK)
    _txt(d, 8, 27, '符号的引脚数与封装的焊盘数必须一一对应，否则更新 PCB 时报错。',
         8, FONT, DARK)
    _txt(d, 8, 12, '常见错误：符号画 0402、实物买 0603；连接器封装引脚顺序镜像。',
         8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：ERC 引脚类型

def sch_erc():
    """ERC 引脚类型冲突矩阵（常见组合）。"""
    d = Drawing(W, 224)
    types = ['输出\nOutput', '输入\nInput', '双向\nBidir', '无源\nPassive',
             '电源输入\nPwr In', '电源输出\nPwr Out']
    # 0 = 正常, 1 = 警告, 2 = 错误
    m = [
        [2, 0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 2],
    ]
    cs, x0, y0 = 46, 96, 214 - 34
    for j, t in enumerate(types):
        for k, ln in enumerate(t.split('\n')):
            _txt(d, x0 + j * cs + cs / 2, y0 + 6 - k * 9, ln,
                 6.8, BOLD if k == 0 else FONT, DARK if k == 0 else GREY, 'middle')
    y = y0 - 12
    for i, t in enumerate(types):
        y -= cs * 0.62
        for k, ln in enumerate(t.split('\n')):
            _txt(d, x0 - 6, y + 14 - k * 9, ln, 6.8,
                 BOLD if k == 0 else FONT, DARK if k == 0 else GREY, 'end')
        for j in range(len(types)):
            v = m[i][j]
            fill = {0: colors.HexColor('#e8f5ec'), 1: colors.HexColor('#fdf6e6'),
                    2: colors.HexColor('#fdeaea')}[v]
            edge = {0: GREEN, 1: AMBER, 2: RED}[v]
            d.add(Rect(x0 + j * cs, y, cs - 3, cs * 0.62 - 3,
                       fillColor=fill, strokeColor=edge, strokeWidth=0.7))
            _txt(d, x0 + j * cs + (cs - 3) / 2, y + 8,
                 {0: '✓', 1: '!', 2: '×'}[v], 9, BOLD, edge, 'middle')

    ly = 30
    for i, (c, t) in enumerate(((GREEN, '✓ 正常'), (AMBER, '! 警告'), (RED, '× 错误'))):
        _txt(d, 8 + i * 76, ly, t, 8, BOLD, c)
    _txt(d, 8, 16, '两个输出引脚直接相连是硬错误（会短路）；电源输出对电源输出同理。',
         8, FONT, DARK)
    _txt(d, 8, 4, '电源网络必须有至少一个「电源输出」或 PWR_FLAG，否则报「电源未驱动」。',
         8, BOLD, RED)
    return d


# ---------------------------------------------------------------- 图：OCXO 焊盘脚位

def ocxo_pinout():
    """U2 焊盘实测坐标与引脚功能（俯视，坐标取自 GPSDO.kicad_pcb）。"""
    d = Drawing(W, 250)
    K = 6.6                                        # mm -> pt
    x0, y0 = 132, 186                              # 焊盘 1 的位置
    # 壳体轮廓（丝印 -3.25 ~ +22.25 mm，约 25.5 mm 见方）
    _box(d, x0 - 3.25 * K, y0 - 22.25 * K, 25.5 * K, 25.5 * K,
         colors.HexColor('#eef2f6'), colors.HexColor('#8fa3b4'), 1.0, r=3)
    _txt(d, x0 + 9.5 * K, y0 - 11 * K, 'OCXO', 11, BOLD, colors.HexColor('#9fb0bf'), 'middle')
    _txt(d, x0 + 9.5 * K, y0 - 14 * K, '25.4 x 25.4 mm', 7.5, FONT,
         colors.HexColor('#9fb0bf'), 'middle')

    pads = [('1', 'RF 输出', 0, 0, ACCENT, 'end'),
            ('2', 'GND', 0, -9.5, GREY, 'end'),
            ('3', 'VCTRL (EFC)', 0, -19, RED, 'end'),
            ('4', 'VREF 未接', 19, -19, GREY, 'start'),
            ('5', 'VCC 供电', 19, 0, AMBER, 'start')]
    for num, name, px, py, col, anc in pads:
        cx, cy = x0 + px * K, y0 + py * K
        d.add(Rect(cx - 6, cy - 6, 12, 12, fillColor=colors.white,
                   strokeColor=col, strokeWidth=1.4, rx=2, ry=2))
        _txt(d, cx, cy - 3, num, 8.5, BOLD, col, 'middle')
        lx = cx - 13 if anc == 'end' else cx + 13
        _txt(d, lx, cy + 1, name, 8.5, BOLD, col, anc)
        _txt(d, lx, cy - 9, '(%g, %g)' % (px, py), 7.5, FONT, GREY, anc)

    # 尺寸标注：横向 19.0 mm
    dy = y0 + 5.6 * K
    d.add(Line(x0, dy, x0 + 19 * K, dy, strokeColor=ACCENT, strokeWidth=0.8))
    for xx in (x0, x0 + 19 * K):
        d.add(Line(xx, dy - 4, xx, dy + 4, strokeColor=ACCENT, strokeWidth=0.8))
    _txt(d, x0 + 9.5 * K, dy + 7, '19.0 mm 引脚网格', 8, BOLD, ACCENT, 'middle')
    # 尺寸标注：纵向 9.5 mm
    dx = x0 - 8.0 * K
    d.add(Line(dx, y0, dx, y0 - 9.5 * K, strokeColor=ACCENT, strokeWidth=0.8))
    for yy in (y0, y0 - 9.5 * K):
        d.add(Line(dx - 4, yy, dx + 4, yy, strokeColor=ACCENT, strokeWidth=0.8))
    _txt(d, dx - 6, y0 - 5.4 * K, '9.5', 8, BOLD, ACCENT, 'end')

    # 右侧要点
    tx, ty = 322, 196
    _txt(d, tx, ty, '焊盘 1.5 mm，钻孔 1.0 mm', 8, FONT, DARK)
    _txt(d, tx, ty - 15, '安装在 PCB 底面 (B.Cu)', 8, FONT, DARK)
    _txt(d, tx, ty - 30, '排布：一边 3 脚 + 对边 2 脚', 8, FONT, DARK)
    _txt(d, tx, ty - 52, '选型时必须逐点比对', 8.5, BOLD, RED)
    _txt(d, tx, ty - 66, 'datasheet 的底视图：', 8.5, BOLD, RED)
    for i, s in enumerate(('几何位置对上', '引脚功能顺序对上', '引脚直径能穿过 1.0 mm 孔')):
        _txt(d, tx + 6, ty - 84 - i * 14, '- ' + s, 8, FONT, GREY)
    _txt(d, tx, ty - 140, '四角 4 脚 + 中心 1 脚的', 8, FONT, RED)
    _txt(d, tx, ty - 153, '另一大类脚位与本板不兼容', 8, FONT, RED)
    return d


# ---------------------------------------------------------------- 图：OCXO 三条链路

def ocxo_chain():
    """OCXO 的供电、控制、输出三条链路及各自的瓶颈。"""
    d = Drawing(W, 250)
    bw, bh = 88, 26

    def chain(y, title, tcol, items, note):
        _txt(d, 2, y + bh + 12, title, 9, BOLD, tcol)
        x = 2
        for i, (top, bot) in enumerate(items):
            _box(d, x, y, bw, bh, colors.white, tcol, 1.0, r=3)
            _txt(d, x + bw / 2, y + bh - 11, top, 8, BOLD, DARK, 'middle')
            _txt(d, x + bw / 2, y + 5, bot, 7, FONT, GREY, 'middle')
            if i < len(items) - 1:
                _arrow(d, x + bw + 1, y + bh / 2, x + bw + 17, y + bh / 2, tcol, .9)
            x += bw + 18
        _txt(d, 2, y - 12, note, 8, BOLD, RED)

    chain(196, '供电链路', AMBER,
          [('电池 / USB', '3.0-4.4 V'), ('BQ25890', 'SYS 轨'),
           ('TPS7A8901', '双路超低噪 LDO'), ('+3.3/+5V', 'OCXO VCC')],
          '瓶颈：LDO 输入即 SYS，结构上做不出 5 V；单通道约 500 mA，对应 3.3 V 下 1.65 W 上限')

    chain(114, '控制链路 (EFC)', ACCENT,
          [('MCU PWM', '16 bit @2.6 kHz'), ('R4 20k / C1 10u', 'fc = 0.8 Hz'),
           ('R5 20k / C2 10u', '二阶'), ('VCTL', '0-3.3 V')],
          '瓶颈：源阻抗 40 k 欧，需选高阻 EFC 器件或加运放跟随器；VCTL 同时回读进 MCU 的 ADC')

    chain(32, '输出链路', GREEN,
          [('OCXO RF', '必须是方波'), ('R6 180 / R24 49.9', '分压约 0.72 Vpp'),
           ('LMK1C1102', '1 分 2 缓冲'), ('SMA J2 / MCU', '50 欧走线')],
          '瓶颈：本板无正弦整形电路；分压后幅度是否满足缓冲器输入门限需复核')
    return d


# ---------------------------------------------------------------- 图：GNSS 模组尺寸对比

def gnss_size():
    """主流 GNSS 模组本体尺寸等比对比，颜色区分定时级与导航级。"""
    d = Drawing(W, 236)
    K = 6.4                                        # mm -> pt
    base = 58
    mods = [(4.5, 4.5, 'MIA-M10Q', '导航级', AMBER),
            (10.1, 9.7, 'PX1100T', '定时级', GREEN),
            (12.2, 16.0, 'NEO-M8T / F10T', '定时级', ACCENT),
            (17.0, 22.0, 'ZED-F9T', '定时级', ACCENT)]
    x = 34
    for mw, mh, name, tier, col in mods:
        w, h = mw * K, mh * K
        _box(d, x, base, w, h, colors.white, col, 1.3, r=2)
        _txt(d, x + w / 2, base + h + 7, '%g x %g' % (mw, mh), 8, BOLD, col, 'middle')
        _txt(d, x + w / 2, base - 13, name, 8.5, BOLD, DARK, 'middle')
        _txt(d, x + w / 2, base - 24, tier, 7.5, FONT, col, 'middle')
        _txt(d, x + w / 2, base + h / 2 - 3, '%.0f' % (mw * mh), 7.5, FONT,
             colors.HexColor('#aab7c2'), 'middle')
        x += w + 46

    # 本板现有焊盘标注
    ny = base + 16.0 * K
    d.add(Line(214, ny + 4, 300, ny + 20, strokeColor=RED, strokeWidth=0.8))
    _txt(d, 302, ny + 17, '本板现有焊盘 12.20 x 16.30 mm / 24 pad', 8, BOLD, RED)
    _txt(d, 302, ny + 5, '与 u-blox NEO 封装尺寸一致', 8, FONT, RED)

    _txt(d, 34, 16, '方框内数字为占板面积 (mm2)。尺寸等比绘制。', 7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：本板 GNSS 链路

def gnss_chain():
    """本板 GNSS 的射频、时间、数据三条链路（取自工程文件实测）。"""
    d = Drawing(W, 236)
    bw, bh = 88, 26

    def chain(y, title, tcol, items, note):
        _txt(d, 2, y + bh + 12, title, 9, BOLD, tcol)
        x = 2
        for i, (top, bot) in enumerate(items):
            _box(d, x, y, bw, bh, colors.white, tcol, 1.0, r=3)
            _txt(d, x + bw / 2, y + bh - 11, top, 8, BOLD, DARK, 'middle')
            _txt(d, x + bw / 2, y + 5, bot, 7, FONT, GREY, 'middle')
            if i < len(items) - 1:
                _arrow(d, x + bw + 1, y + bh / 2, x + bw + 17, y + bh / 2, tcol, .9)
            x += bw + 18
        _txt(d, 2, y - 12, note, 8, BOLD, RED)

    chain(182, '射频链路', GREEN,
          [('有源天线', '需外部供电'), ('IPEX 座 U4', '2.7 x 2.7 mm'),
           ('L1 33nH 偏置', 'ANT_POWER pin9'), ('模组 RF_IN', 'pin 11')],
          '天线偏置由模组的 ANT_POWER 引脚经 L1 供出到 VANT，换料时必须确认新模组有同样的天线供电引脚')

    chain(104, '时间链路', ACCENT,
          [('模组 PPS', 'pin 3'), ('R1 100 欧', '串联限流'),
           ('MCU 32bit TIM', 'U1 pin 5 区'), ('闸门计数', '频差测量')],
          '这条链路的真实精度由模组是否支持定时模式与锯齿波修正决定，不由走线决定')

    chain(26, '数据与备电', AMBER,
          [('模组 UART0', 'pin 20 / 21'), ('R2 / R3 33 欧', '串联匹配'),
           ('MCU USART', 'NMEA 解析'), ('V_BCKP pin22', 'R7 470 + C5 1uF')],
          'V_BCKP 当前只经 R7 从 3.3V 取电，没有电池或超级电容，断电后星历丢失，每次都是冷启动')
    return d


# ---------------------------------------------------------------- 图：ADEV 对比

def gpsdo_adev():
    """各类振荡器与 GPS 1PPS 的典型 ADEV，以及 GPSDO 输出的合成包络。"""
    from math import log10
    d = Drawing(W, 306)
    X0, Y0, XW, YH = 62, 96, 372, 186             # 绘图区
    TMIN, TMAX = 0, 6                              # log10(tau): 1 s .. 1e6 s
    AMIN, AMAX = -13, -8                           # log10(ADEV)

    def px(t):
        return X0 + (log10(t) - TMIN) / (TMAX - TMIN) * XW

    def py(a):
        return Y0 + (log10(a) - AMIN) / (AMAX - AMIN) * YH

    # 网格
    for e in range(TMIN, TMAX + 1):
        x = px(10 ** e)
        d.add(Line(x, Y0, x, Y0 + YH, strokeColor=colors.HexColor('#e2e8ee'),
                   strokeWidth=0.5))
        lab = {0: '1 s', 1: '10 s', 2: '100 s', 3: '1 ks', 4: '10 ks',
               5: '100 ks', 6: '1 Ms'}[e]
        _txt(d, x, Y0 - 12, lab, 7.5, FONT, GREY, 'middle')
    for e in range(AMIN, AMAX + 1):
        y = py(10.0 ** e)
        d.add(Line(X0, y, X0 + XW, y, strokeColor=colors.HexColor('#e2e8ee'),
                   strokeWidth=0.5))
        _txt(d, X0 - 6, y - 3, '1e%d' % e, 7.5, FONT, GREY, 'end')
    _box(d, X0, Y0, XW, YH, colors.transparent if hasattr(colors, 'transparent')
         else None, colors.HexColor('#9fb0bf'), 0.8)
    _txt(d, X0 + XW / 2, Y0 - 26, '取样时间 tau', 8.5, BOLD, DARK, 'middle')
    _txt(d, X0 - 46, Y0 + YH + 8, 'ADEV', 8.5, BOLD, DARK)

    curves = [
        ('GPS 1PPS (定时级+锯齿修正)', AMBER, 1.3, 0,
         [(1, 2e-8), (10, 2e-9), (100, 2e-10), (1e3, 2e-11), (1e4, 2e-12),
          (1e5, 4e-13), (1e6, 2e-13)]),
        ('普通 TCXO 自由运行', colors.HexColor('#b0b8c0'), 1.0, 1,
         [(1, 5e-10), (10, 5e-10), (100, 1e-9), (300, 2e-9)]),
        ('超稳 MEMS 自由运行', colors.HexColor('#16a085'), 1.0, 1,
         [(1, 2e-10), (10, 1.5e-10), (100, 2e-10), (1e3, 5e-10), (1e4, 2e-9)]),
        ('普通 OCXO 自由运行', RED, 1.1, 1,
         [(1, 1e-11), (10, 8e-12), (100, 1e-11), (1e3, 3e-11), (1e4, 1e-10),
          (1e5, 8e-10), (3e5, 2e-9)]),
        ('高端 OCXO / 双恒温 自由运行', colors.HexColor('#8e44ad'), 1.0, 1,
         [(1, 1e-12), (10, 8e-13), (100, 1e-12), (1e3, 3e-12), (1e4, 2e-11),
          (1e5, 1e-10), (1e6, 8e-10)]),
        ('铷原子钟 自由运行', colors.HexColor('#2980b9'), 1.0, 1,
         [(1, 2e-11), (10, 7e-12), (100, 2e-12), (1e3, 1e-12), (1e4, 1e-12),
          (1e5, 2e-12), (1e6, 1e-11)]),
        ('GPSDO 输出 (普通 OCXO 被驯服)', ACCENT, 2.4, 0,
         [(1, 1e-11), (10, 8e-12), (100, 1e-11), (1e3, 2e-11), (2e3, 1.4e-11),
          (1e4, 2e-12), (1e5, 4e-13), (1e6, 2e-13)]),
    ]
    for name, col, sw, dash, pts in curves:
        p = []
        for t, a in pts:
            p += [px(t), py(a)]
        pl = PolyLine(p, strokeColor=col, strokeWidth=sw)
        if dash:
            pl.strokeDashArray = (3, 2)
        d.add(pl)

    # 交越点标注
    xc = px(1.6e3)
    d.add(Line(xc, Y0, xc, py(6e-11), strokeColor=DARK, strokeWidth=0.7,
               strokeDashArray=(2, 2)))
    _txt(d, xc + 4, py(8e-11), '交越点 tau_c', 7.5, BOLD, DARK)
    _txt(d, xc + 4, py(4e-11), '由环路时间常数决定', 7, FONT, GREY)

    # 图例
    ly = 56
    for i, (name, col, sw, dash, _) in enumerate(curves):
        cx = 8 + (i % 2) * 238
        cy = ly - (i // 2) * 14
        ln = Line(cx, cy + 3, cx + 20, cy + 3, strokeColor=col,
                  strokeWidth=max(sw, 1.2))
        if dash:
            ln.strokeDashArray = (3, 2)
        d.add(ln)
        _txt(d, cx + 25, cy, name, 7.5, BOLD if sw > 2 else FONT, DARK)
    _txt(d, 8, 4, '典型量级示意，非实测曲线。要点：GPSDO 输出在短 tau 跟随 OCXO，在长 tau 跟随 GPS，两者交越处由环路带宽决定。',
         7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：三种 TIC 架构

def gpsdo_tic():
    """开源 GPSDO 用过的三种时间差测量架构及其分辨率。"""
    d = Drawing(W, 236)
    cards = [
        ('MCU 定时器直接捕获', '5.9 ns @170 MHz', AMBER,
         ['1PPS 触发定时器输入捕获，', '读 OCXO 时钟的计数值', '',
          '分辨率 = 1 / f_clk', '', '代表：AndrewBCN/STM32-GPSDO', '本项目 v1.0 当前方案', '',
          '优：零外部器件', '缺：分辨率被主频锁死']),
        ('模拟相位比较', '约 1 ns', ACCENT,
         ['HC390 分频 + HC4046 相位比较，', '输出经二极管与 RC 网络',
          '直接进 MCU 的 10 bit ADC', '', '量程 1 us，分辨率约 1 ns', '',
          '代表：Lars Walenius GPSDO', 'jimharman/Arduino-GPSDO', '',
          '优：几个无源件做到 1 ns', '缺：需线性化标定，有温漂']),
        ('专用 TDC 芯片', '55 - 60 ps', GREEN,
         ['TI TDC7200 直接测量两个', '边沿之间的时间间隔', '',
          '单次分辨率 55 ps，', '长观测区间约 60 ps 为其极限', '',
          '代表：thinkfat 的 STM32+TDC7200', 'Carsten Andrich 的 STM32G4 方案', 'TAPR TICC 计数器', '',
          '优：分辨率最高，无需标定', '缺：多一颗芯片，固件复杂']),
    ]
    cw, gap = 148, 14
    x = 2
    for title, res, col, lines in cards:
        _box(d, x, 20, cw, 200, colors.white, col, 1.2, r=4)
        d.add(Rect(x, 192, cw, 28, fillColor=col, strokeColor=col))
        _txt(d, x + cw / 2, 201, title, 9, BOLD, colors.white, 'middle')
        _txt(d, x + cw / 2, 170, res, 13, BOLD, col, 'middle')
        y = 152
        for ln in lines:
            if ln:
                _txt(d, x + 9, y, ln, 7.2, FONT, DARK)
            y -= 11
        x += cw + gap
    _txt(d, 2, 6, '分辨率指时间差测量环节的分辨率，不等于 GPSDO 输出的 ADEV。', 7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：分辨率横向对比

def gpsdo_res_bar():
    """各开源 GPSDO 的时间差测量分辨率，对数横轴。"""
    from math import log10
    d = Drawing(W, 206)
    X0, BW = 186, 250
    LO, HI = -11, -6.6                             # log10(秒)：10 ps .. 250 ns

    def px(v):
        return X0 + (log10(v) - LO) / (HI - LO) * BW

    items = [('TAPR TICC / TDC7200 架构', 55e-12, GREEN),
             ('thinkfat STM32 + TDC7200', 55e-12, GREEN),
             ('Carsten Andrich STM32G4 方案', 50e-12, GREEN),
             ('Lars Walenius GPSDO', 1e-9, ACCENT),
             ('本项目 v1.0 (10 MHz 作时基，单次)', 100e-9, RED),
             ('AndrewBCN STM32-GPSDO', 10e-9, AMBER)]
    y = 164
    for name, v, col in items:
        w = px(v) - X0
        d.add(Rect(X0, y, max(w, 2), 15, fillColor=col, strokeColor=col))
        _txt(d, X0 - 8, y + 4, name, 8, FONT, DARK, 'end')
        lab = ('%.0f ps' % (v * 1e12)) if v < 1e-9 else ('%.0f ns' % (v * 1e9))
        _txt(d, px(v) + 6, y + 4, lab, 8, BOLD, col)
        y -= 24
    for e in range(LO, -6):
        x = px(10.0 ** e)
        d.add(Line(x, 12, x, 180, strokeColor=colors.HexColor('#e2e8ee'),
                   strokeWidth=0.5))
        lab = {-11: '10 ps', -10: '100 ps', -9: '1 ns', -8: '10 ns',
               -7: '100 ns'}.get(e, '')
        if lab:
            _txt(d, x, 2, lab, 7.5, FONT, GREY, 'middle')
    _txt(d, X0, 190, '横轴为对数刻度，越短越好', 7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：v1.1 双轨路线

def v11_roadmap():
    """v1.1 的硬件改板轨与固件里程碑轨，以及两者的依赖关系。"""
    d = Drawing(W, 262)

    # ---- 硬件轨 ----
    _txt(d, 2, 236, '硬件轨（依赖采购与打样周期）', 9, BOLD, RED)
    hw = [('HW-1', '选型与采购'), ('HW-2', '原理图与 PCB 改动'),
          ('HW-3', '打样与焊接'), ('HW-4', '硬件验收实测')]
    hx, hw_w, hgap, hy = 30, 104, 8, 182
    for i, (tag, name) in enumerate(hw):
        x = hx + i * (hw_w + hgap)
        _box(d, x, hy, hw_w, 40, colors.white, RED, 1.2, r=3)
        d.add(Rect(x, hy + 28, hw_w, 12, fillColor=RED, strokeColor=RED))
        _txt(d, x + hw_w / 2, hy + 31, tag, 7.5, BOLD, colors.white, 'middle')
        _txt(d, x + hw_w / 2, hy + 12, name, 8, BOLD, DARK, 'middle')
        if i < len(hw) - 1:
            _arrow(d, x + hw_w + 1, hy + 20, x + hw_w + hgap - 1, hy + 20, RED, .9)

    # ---- 固件轨 ----
    _txt(d, 2, 124, '固件轨（纯软件，不占用采购周期）', 9, BOLD, GREEN)
    fw = [('M0', '构建系统', 0), ('M1', '板级校正', 0), ('M2', '基础驱动', 0),
          ('M3', '时间测量', 0), ('M4', '锯齿修正', 1), ('M5', '控制环', 0),
          ('M6', '数据记录', 0), ('M7', '守时启动', 0)]
    fx, fw_w, fgap, fy = 30, 52, 4, 66
    for i, (tag, name, dep) in enumerate(fw):
        x = fx + i * (fw_w + fgap)
        col = AMBER if dep else GREEN
        _box(d, x, fy, fw_w, 40, colors.white, col, 1.2, r=3)
        d.add(Rect(x, fy + 28, fw_w, 12, fillColor=col, strokeColor=col))
        _txt(d, x + fw_w / 2, fy + 31, tag, 7.5, BOLD, colors.white, 'middle')
        _txt(d, x + fw_w / 2, fy + 12, name, 7, BOLD, DARK, 'middle')
        if i < len(fw) - 1:
            _arrow(d, x + fw_w + 0.5, fy + 20, x + fw_w + fgap - 0.5, fy + 20, col, .8)

    # ---- 依赖箭头：M4 需要定时级 GNSS 模组到货 ----
    m4x = fx + 4 * (fw_w + fgap) + fw_w / 2
    d.add(Line(hx + hw_w / 2, hy - 1, hx + hw_w / 2, 150,
               strokeColor=AMBER, strokeWidth=0.9, strokeDashArray=(3, 2)))
    d.add(Line(hx + hw_w / 2, 150, m4x, 150,
               strokeColor=AMBER, strokeWidth=0.9, strokeDashArray=(3, 2)))
    _arrow(d, m4x, 150, m4x, fy + 41, AMBER, .9)
    _txt(d, m4x + 6, 152, 'M4 需要定时级 GNSS 模组到货', 7.5, BOLD, AMBER)

    # ---- 图例 ----
    for i, (c, t) in enumerate(((GREEN, '可在现有 v1.0 板上立即开始'),
                                (AMBER, '需等器件到货'),
                                (RED, '需等打样'))):
        bx = 30 + i * 150
        d.add(Rect(bx, 26, 14, 9, fillColor=colors.white, strokeColor=c, strokeWidth=1.2))
        _txt(d, bx + 19, 27, t, 7.5, FONT, GREY)
    _txt(d, 30, 8, '要点：固件的 M0 到 M3、M5 到 M7 全部不依赖改板，可与硬件轨完全并行。',
         7.5, BOLD, DARK)
    return d


# ======================================================= Carsten Andrich 方案图解
# 以下各图用于 docs/hardware/Carsten-Andrich-GNSSDO方案图解.md。
# 电路细节取自作者 2022-08-05（v1）与 2022-08-11（v2）两版原理图及 v2 版图。

CLK = ACCENT                                   # 10 MHz 时钟
PPS = RED                                      # 脉冲
ANA = GREEN                                    # 模拟调谐电压
BUS = colors.HexColor('#7f8c8d')               # 数字总线
SEN = colors.HexColor('#8e44ad')               # 传感器
TDC = colors.HexColor('#16a085')               # TDC 相关
MCU_C = colors.HexColor('#34495e')
LIGHT = colors.HexColor('#e2e8ee')


def _wire(d, pts, col=DARK, sw=0.8, dash=None):
    pl = PolyLine(pts, strokeColor=col, strokeWidth=sw)
    if dash:
        pl.strokeDashArray = dash
    d.add(pl)


def _dot(d, x, y, col=DARK, r=1.8):
    d.add(Circle(x, y, r, fillColor=col, strokeColor=col, strokeWidth=0.5))


def _blk(d, x, y, w, h, title, lines=(), col=ACCENT, size=7):
    """带色条标题的功能块。"""
    _box(d, x, y, w, h, colors.white, col, 1.1, r=3)
    d.add(Rect(x, y + h - 13, w, 13, fillColor=col, strokeColor=col))
    _txt(d, x + w / 2, y + h - 9.5, title, 7.8, BOLD, colors.white, 'middle')
    for i, ln in enumerate(lines):
        _txt(d, x + 5, y + h - 24 - i * 10, ln, size, FONT, DARK)


def _res(d, x1, y1, x2, y2, col=DARK):
    """两点间的电阻（矩形体），只支持水平或竖直。"""
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    if abs(y2 - y1) < 0.01:
        _wire(d, [min(x1, x2), cy, cx - 8, cy], col)
        _wire(d, [cx + 8, cy, max(x1, x2), cy], col)
        d.add(Rect(cx - 8, cy - 3, 16, 6, fillColor=colors.white,
                   strokeColor=col, strokeWidth=0.9))
    else:
        _wire(d, [cx, max(y1, y2), cx, cy + 8], col)
        _wire(d, [cx, cy - 8, cx, min(y1, y2)], col)
        d.add(Rect(cx - 3, cy - 8, 6, 16, fillColor=colors.white,
                   strokeColor=col, strokeWidth=0.9))


def _cap(d, x1, y1, x2, y2, col=DARK):
    """两点间的电容（两块极板），只支持水平或竖直。"""
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    g, p = 2.2, 6
    if abs(y2 - y1) < 0.01:
        _wire(d, [min(x1, x2), cy, cx - g, cy], col)
        _wire(d, [cx + g, cy, max(x1, x2), cy], col)
        for xx in (cx - g, cx + g):
            d.add(Line(xx, cy - p, xx, cy + p, strokeColor=col, strokeWidth=1.4))
    else:
        _wire(d, [cx, max(y1, y2), cx, cy + g], col)
        _wire(d, [cx, cy - g, cx, min(y1, y2)], col)
        for yy in (cy - g, cy + g):
            d.add(Line(cx - p, yy, cx + p, yy, strokeColor=col, strokeWidth=1.4))


def _gnd(d, x, y, col=DARK):
    """接地符号，(x, y) 为连接点。"""
    d.add(Line(x, y, x, y - 4, strokeColor=col, strokeWidth=0.8))
    for i, hw in enumerate((5, 3.2, 1.4)):
        yy = y - 4 - i * 2.2
        d.add(Line(x - hw, yy, x + hw, yy, strokeColor=col, strokeWidth=0.8))


def _tri(d, x, y, w, h, col=DARK, fill=colors.HexColor('#fffbe6')):
    """朝右的放大器三角形，(x, y) 为左边中点。"""
    d.add(Polygon([x, y + h / 2, x, y - h / 2, x + w, y],
                  fillColor=fill, strokeColor=col, strokeWidth=1))


def _sma(d, x, y, col=DARK):
    d.add(Circle(x, y, 6, fillColor=colors.white, strokeColor=col, strokeWidth=1.1))
    d.add(Circle(x, y, 1.8, fillColor=col, strokeColor=col))


# ---------------------------------------------------------------- 图：应用场景

def ca_usecase():
    """固定基准站 + 移动车辆上的 GNSSDO，做车辆之间的相对时间同步。"""
    d = Drawing(W, 236)
    # 卫星
    for i, sx in enumerate((168, 250, 332, 414)):
        sy = 220 - (i % 2) * 6
        d.add(Rect(sx - 4, sy - 4, 8, 8, fillColor=GREY, strokeColor=GREY))
        for px0 in (sx - 16, sx + 6):
            d.add(Rect(px0, sy - 2, 10, 4, fillColor=colors.HexColor('#a9c1d9'),
                       strokeColor=GREY, strokeWidth=0.4))
    _txt(d, 6, 214, 'GNSS 卫星（基准站与车辆共视）', 7.5, FONT, GREY)

    # 基准站与天线
    _blk(d, 6, 92, 128, 70, '固定基准站', ['ZED-F9T 时间模式', '已测量坐标，1D 授时解',
                                           '持续输出 RTCM 3 MSM7'], GREEN)
    _wire(d, [70, 162, 70, 178])
    d.add(Polygon([61, 188, 79, 188, 70, 178], fillColor=colors.white,
                  strokeColor=DARK, strokeWidth=0.8))

    # 无线链路
    _wire(d, [134, 127, 182, 127], GREEN, 1.1, (4, 2))
    _wire(d, [182, 59, 182, 171], GREEN, 1.1, (4, 2))
    _txt(d, 138, 131, '无线链路', 7, BOLD, GREEN)
    _txt(d, 138, 116, '差分修正', 7, FONT, GREEN)

    for i, (vy, tag) in enumerate(((149, 'A'), (93, 'B'), (37, 'C'))):
        _arrow(d, 182, vy + 22, 206, vy + 22, GREEN, 1.0)
        _blk(d, 208, vy, 152, 44, '车辆 %s：GNSSDO' % tag,
             ['ZED-F9T 差分授时 + 低 g 敏感 OCXO', '输出 10 MHz 与稳定脉冲'], ACCENT)
        _arrow(d, 360, vy + 22, 378, vy + 22, ACCENT, 1.0)
        _blk(d, 380, vy, 98, 44, '被同步设备', ['分布式 SDR 相干采样', '毫米波变频器'], SEN)

    _txt(d, 6, 20, '目标：10 km 半径内、移动中相对时间误差 < 10 ns，期望 < 1 ns。'
         '1 ns 对应电波传播约 30 cm。', 7.5, BOLD, DARK)
    _txt(d, 6, 6, '只要求车辆之间相对同步，不关心绝对 UTC 误差。作者用过的 Ministd、LC_XO、'
         'FS740 在移动中均不达标。', 7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：系统总框图

def ca_system():
    """整机功能块与信号流向，颜色区分信号类型。"""
    d = Drawing(W, 330)
    # ---- 功能块 ----
    _blk(d, 4, 196, 86, 66, 'RCB-F9T 板', ['u-blox ZED-F9T', '定时级 + 差分授时',
                                            'TP1 / TP2 / UART'], PPS)
    _blk(d, 124, 196, 82, 66, 'TDC7200', ['单次约 55 ps', 'START：GNSS 脉冲',
                                          'STOP/CLK：10 MHz'], TDC)
    _blk(d, 236, 140, 122, 122, 'STM32G474RE',
         ['SYSCLK 170 MHz', '（由 OCXO 10 MHz 倍频）', '', 'TIM2 32 bit 捕获 5.88 ns',
          'HRTIM 脉冲微调 184 ps', 'SPI1 / SPI2 / I2C3 / UART4', '数字环路与 qErr 修正',
          'USB 调试与数据'], MCU_C)
    _blk(d, 4, 40, 74, 56, 'LMK1C1103', ['1 分 3 缓冲', '通道偏斜 <= 50 ps',
                                          '无分频无同步器'], CLK)
    _blk(d, 100, 40, 84, 56, 'OCXO 10 MHz', ['Abracon AOCJY', '塑料罩挡气流',
                                             '罩内 TMP117 测温'], CLK)
    _blk(d, 206, 40, 92, 56, '有源低通', ['OPA189 二阶 SK', 'v1 约 1 Hz / v2 约 10 Hz',
                                         '+ 无源 RC 159 Hz'], ANA)
    _blk(d, 320, 40, 66, 56, '调谐 DAC', ['AD5542A 16 bit', 'ADR4533 3.3 V',
                                         '或 OCXO VREF'], ANA)

    # ---- 输出驱动 ----
    _box(d, 398, 52, 80, 210, colors.white, DARK, 1.1, r=3)
    d.add(Rect(398, 249, 80, 13, fillColor=DARK, strokeColor=DARK))
    _txt(d, 438, 252.5, 'BUF602 x5 + SMA', 7.8, BOLD, colors.white, 'middle')
    for y, name, col in ((230, 'F9T TP2 原始', PPS), (196, '稳定脉冲 1', PPS),
                         (168, '稳定脉冲 2', PPS), (96, '10 MHz 1', CLK),
                         (68, '10 MHz 2', CLK)):
        _txt(d, 404, y - 3, name, 7, FONT, DARK)
        _sma(d, 466, y, col)
    _txt(d, 438, 136, '49.9 欧源端匹配', 6.8, FONT, GREY, 'middle')
    _txt(d, 438, 125, '可驱动 50 欧负载', 6.8, FONT, GREY, 'middle')

    # ---- GNSS 侧 ----
    _arrow(d, 90, 228, 123, 228, PPS, 1.1)
    _dot(d, 106, 228, PPS)
    _wire(d, [106, 228, 106, 280, 272, 280], PPS, 1.1)
    _arrow(d, 272, 280, 272, 263, PPS, 1.1)
    _txt(d, 112, 283, 'TP1：TDC START 与 TIM2_CH4 捕获', 7, BOLD, PPS)
    _wire(d, [64, 262, 64, 296, 318, 296], BUS, 1.0)
    _arrow(d, 318, 296, 318, 263, BUS, 1.0)
    _txt(d, 112, 299, 'UART4：UBX 配置、TIM-TP（qErr）、RTCM 修正数据', 7, FONT, BUS)
    _wire(d, [24, 262, 24, 312, 390, 312, 390, 230], PPS, 1.0, (3, 2))
    _arrow(d, 390, 230, 397, 230, PPS, 1.0)
    _txt(d, 112, 315, 'TP2：原始 GNSS 脉冲直接送 SMA，作对照', 7, FONT, PPS)

    # ---- MCU 侧 ----
    _wire(d, [206, 236, 236, 236], BUS, 1.0)
    _txt(d, 221, 240, 'SPI2', 6.5, FONT, BUS, 'middle')
    _txt(d, 221, 226, 'INTB', 6.5, FONT, BUS, 'middle')
    _arrow(d, 358, 196, 397, 196, PPS, 1.1)
    _dot(d, 378, 196, PPS)
    _wire(d, [378, 196, 378, 168], PPS, 1.1)
    _arrow(d, 378, 168, 397, 168, PPS, 1.1)
    _txt(d, 362, 200, 'PA9', 6.5, BOLD, PPS)
    _arrow(d, 353, 140, 353, 97, BUS, 1.0)
    _txt(d, 356, 116, 'SPI1', 6.5, FONT, BUS)
    _wire(d, [300, 140, 300, 114, 160, 114], SEN, 1.0)
    _arrow(d, 160, 114, 160, 97, SEN, 1.0)
    _txt(d, 270, 105, 'I2C3', 6.5, FONT, SEN)

    # ---- 时钟分配 ----
    _wire(d, [60, 96, 60, 128, 250, 128], CLK, 1.2)
    _arrow(d, 250, 128, 250, 139, CLK, 1.2)
    _txt(d, 66, 131, '10MHZ_MCU：送 PF0（HSE 旁路）', 7, BOLD, CLK)
    _wire(d, [30, 96, 30, 170, 165, 170], CLK, 1.2)
    _arrow(d, 165, 170, 165, 195, CLK, 1.2)
    _txt(d, 36, 173, '10MHZ_TDC：CLOCK + STOP', 7, BOLD, CLK)
    _wire(d, [40, 40, 40, 26, 390, 26, 390, 96], CLK, 1.2)
    _arrow(d, 390, 96, 397, 96, CLK, 1.2)
    _dot(d, 390, 68, CLK)
    _arrow(d, 390, 68, 397, 68, CLK, 1.2)
    _txt(d, 200, 29, '10MHZ_OUT', 7, BOLD, CLK)

    # ---- 调谐链路 ----
    _arrow(d, 320, 68, 299, 68, ANA, 1.3)
    _arrow(d, 206, 68, 185, 68, ANA, 1.3)
    _txt(d, 195, 73, 'VCTL', 6.5, BOLD, ANA, 'middle')
    _arrow(d, 100, 68, 79, 68, CLK, 1.3)

    for i, (c, t) in enumerate(((CLK, '10 MHz 时钟'), (PPS, '脉冲'), (ANA, '模拟调谐'),
                                (BUS, '数字总线'), (SEN, '传感器'), (TDC, 'TDC'))):
        bx = 6 + i * 80
        d.add(Line(bx, 9, bx + 16, 9, strokeColor=c, strokeWidth=1.8))
        _txt(d, bx + 21, 6, t, 7.5, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：时钟与脉冲分配

def ca_clock_tree():
    """10 MHz 与各路脉冲的完整路径，按相干域与异步域分区。"""
    d = Drawing(W, 300)
    bw, bh, gap = 76, 26, 18

    def bx(i):
        return 4 + i * (bw + gap)

    d.add(Rect(0, 126, W, 168, fillColor=colors.HexColor('#eef4fb'), strokeColor=None))
    d.add(Rect(0, 20, W, 100, fillColor=colors.HexColor('#fdf1ec'), strokeColor=None))
    _txt(d, W - 4, 282, 'OCXO 相干时钟域', 8.5, BOLD, CLK, 'end')
    _txt(d, W - 4, 108, 'GNSS 异步域', 8.5, BOLD, PPS, 'end')

    def chain(y, title, col, items):
        _txt(d, 4, y + bh + 5, title, 8, BOLD, col)
        for i, it in enumerate(items):
            if it is None:
                continue
            top, bot = it
            x = bx(i)
            _box(d, x, y, bw, bh, colors.white, col, 1.0, r=3)
            _txt(d, x + bw / 2, y + bh - 10, top, 7.3, BOLD, DARK, 'middle')
            _txt(d, x + bw / 2, y + 4.5, bot, 6.6, FONT, GREY, 'middle')
            if i < len(items) - 1 and items[i + 1] is not None:
                _arrow(d, x + bw + 1, y + bh / 2, x + bw + gap - 1, y + bh / 2, col, 0.9)

    chain(242, 'A. 10 MHz 直接输出', CLK,
          [('OCXO', '10 MHz CMOS'), ('LMK1C1103', 'Y0 / Y1 / Y2'),
           ('BUF602 x2', '49.9 欧源端匹配'), ('SMA x2', '10 MHz 输出')])
    chain(190, 'B. MCU 时钟与脉冲', CLK,
          [None, ('Y1 + R331', '0 欧'), ('PF0 / OSC_IN', 'HSE 旁路输入'),
           ('PLL + TIM2', '170 MHz，5.88 ns'), ('HRTIM -> PA9', '184 ps，PULSE_MCU')])
    chain(138, 'C. TDC 时基', CLK,
          [None, ('Y2 + R332', '0 欧'), ('TDC7200', 'CLOCK + STOP')])
    chain(70, 'D. GNSS 脉冲（被测对象）', PPS,
          [('ZED-F9T TP1', '内部时钟量化'), ('R101', 'PULSE_GNSS')])
    chain(24, 'E. GNSS 原始脉冲直通', PPS,
          [('ZED-F9T TP2', '同一接收机'), ('R102', 'F9T_PULSE_OUT'),
           ('BUF602', '49.9 欧'), ('SMA', '对照用原始脉冲')])

    # LMK 的 Y1 / Y2 分支
    lx = bx(1)
    _arrow(d, lx + 52, 242, lx + 52, 217, CLK, 0.9)
    _txt(d, lx + 56, 228, 'Y1', 6.5, BOLD, CLK)
    _wire(d, [lx + 12, 242, lx + 12, 229, lx - 12, 229, lx - 12, 151], CLK, 0.9)
    _arrow(d, lx - 12, 151, lx - 1, 151, CLK, 0.9)
    _txt(d, lx + 16, 233, 'Y2', 6.5, BOLD, CLK)
    _txt(d, 334, 154, 'TDC 的 CLOCK 与 STOP 经 JP231', 6.8, FONT, CLK)
    _txt(d, 334, 143, '接同一路 10 MHz', 6.8, FONT, CLK)

    # GNSS 脉冲分到 TDC START 与 TIM2_CH4
    y0 = 70 + bh / 2
    _wire(d, [bx(1) + bw, y0, 230, y0], PPS, 1.1)
    _dot(d, 230, y0, PPS)
    _arrow(d, 230, y0, 230, 137, PPS, 1.1)
    _txt(d, 234, 108, 'START', 7, BOLD, PPS)
    _wire(d, [230, y0, 324, y0], PPS, 1.1)
    _arrow(d, 324, y0, 324, 189, PPS, 1.1)
    _txt(d, 328, 108, 'TIM2_CH4 捕获（PB11）', 7, BOLD, PPS)

    _txt(d, 4, 6, '要点：只有 GNSS 脉冲是异步信号。TDC 时基、MCU 定时器、输出脉冲全部来自同一个 10 MHz，'
         '链路中没有 74 系列分频器或同步器。', 7, FONT, DARK)
    return d


# ---------------------------------------------------------------- 图：两级时间测量时序

def ca_tic_timing():
    """TIM2 粗测 + TDC7200 细测的时序，含死区折叠的两种情形。"""
    d = Drawing(W, 290)
    T0, T1, X0, X1 = -20.0, 232.0, 118, 476
    H = 11

    def px(t):
        return X0 + (t - T0) / (T1 - T0) * (X1 - X0)

    def step(y, t_rise, col):
        _wire(d, [px(T0), y, px(t_rise), y, px(t_rise), y + H, px(T1), y + H], col, 1.2)

    for e in (0, 100, 200):
        _wire(d, [px(e), 82, px(e), 250], colors.HexColor('#c9d3dc'), 0.6, (2, 2))
        _txt(d, px(e), 254, '%d ns' % e, 7, FONT, GREY, 'middle')

    # 10 MHz
    pts, lvl = [px(T0), 230], 0
    for t in (0, 50, 100, 150, 200):
        pts += [px(t), 230 + lvl * H]
        lvl = 1 - lvl
        pts += [px(t), 230 + lvl * H]
    pts += [px(T1), 230 + lvl * H]
    _wire(d, pts, CLK, 1.2)
    _txt(d, 4, 232, '10 MHz（CLOCK/STOP）', 7.5, BOLD, CLK)

    # TIM2 计数节拍
    k = -3
    while k * 100 / 17 <= T1:
        t = k * 100 / 17
        if t >= T0:
            d.add(Line(px(t), 204, px(t), 210, strokeColor=MCU_C, strokeWidth=0.6))
        k += 1
    d.add(Line(px(T0), 204, px(T1), 204, strokeColor=MCU_C, strokeWidth=0.6))
    _txt(d, 4, 204, 'TIM2 节拍 5.88 ns', 7.5, BOLD, MCU_C)

    def case(y, tp, label, tau, note, ignored=None):
        d.add(Rect(px(tp), y - 1, px(tp + 12) - px(tp), H + 2,
                   fillColor=colors.HexColor('#f9d5d0'), strokeColor=None))
        step(y, tp, PPS)
        _txt(d, 4, y + 2, label, 7.5, BOLD, PPS)
        # TIM2 捕获点（示意：边沿后第 2 个节拍）
        tc = (math.floor(tp * 17 / 100) + 2) * 100 / 17
        d.add(Polygon([px(tc) - 3, y + H + 9, px(tc) + 3, y + H + 9, px(tc), y + H + 3],
                      fillColor=MCU_C, strokeColor=MCU_C))
        _txt(d, px(tc) + 5, y + H + 4, 't_c', 7, BOLD, MCU_C)
        # TDC 测得的 tau
        by = y - 13
        stop = tp + tau
        d.add(Line(px(tp), by, px(stop), by, strokeColor=TDC, strokeWidth=1.1))
        for xx in (px(tp), px(stop)):
            d.add(Line(xx, by - 3, xx, by + 3, strokeColor=TDC, strokeWidth=1.1))
        _txt(d, (px(tp) + px(stop)) / 2, by - 10, note, 7, BOLD, TDC, 'middle')
        if ignored is not None:
            xi = px(ignored)
            for s in (-1, 1):
                d.add(Line(xi - 4, by - 4 * s, xi + 4, by + 4 * s,
                           strokeColor=RED, strokeWidth=1.3))

    case(166, 37, '情形 A：GNSS 脉冲', 63, 'TDC 读数 tau = 63 ns')
    case(112, 94, '情形 B：GNSS 脉冲', 106,
         'tau = 106 ns：100 ns 处的沿落在 12 ns 死区内被忽略，取下一个沿', ignored=100)

    lines = [('(1) 粗测', 'TIM2 捕获 GNSS 脉冲得 t_c。误差只要小于 +/-50 ns 即可，输入同步带来的固定延迟可一次标定。'),
             ('(2) 细测', 'TDC7200 测 tau：脉冲到其后第一个可用 10 MHz 上升沿，范围 12 ~ 112 ns，红色为 12 ns 死区。'),
             ('(3) 组合', 'k = round((t_c + tau) / 100 ns)，脉冲精确时刻 t = k x 100 ns - tau，分辨率由 TDC 决定。')]
    for i, (h, s) in enumerate(lines):
        _txt(d, 4, 54 - i * 15, h, 7.5, BOLD, DARK)
        _txt(d, 44, 54 - i * 15, s, 7.5, FONT, DARK)
    return d


# ---------------------------------------------------------------- 图：TDC 死区折叠与实测

TDC_DATA = [  # 作者 2022-08-28 在 EEVblog 发布：设定间隔对应的平均读数 (ns) 与标准差 (ps)
    (6.71, 10), (12.54, 13), (18.47, 28), (24.31, 22), (30.14, 26), (36.05, 32),
    (41.92, 35), (47.77, 40), (53.68, 43), (59.57, 47), (71.34, 53), (83.08, 57),
    (94.84, 64), (106.59, 71), (118.37, 80), (147.86, 96), (177.31, 117),
    (206.68, 136), (236.14, 159), (265.53, 178), (294.94, 205), (353.80, 260),
    (412.64, 311), (471.39, 370), (530.29, 425), (589.12, 481), (647.95, 537),
    (706.81, 588), (765.66, 648), (824.37, 703), (883.24, 761), (942.11, 826),
    (1000.94, 872), (1059.80, 917), (1118.67, 967), (1177.35, 1013)]


def _axes(d, X0, Y0, XW, YH, xt, yt, xlab, ylab, fx, fy):
    """线性坐标轴与网格。xt / yt 为刻度值列表，fx / fy 为刻度文本格式。"""
    for v in xt:
        x = X0 + (v - xt[0]) / (xt[-1] - xt[0]) * XW
        d.add(Line(x, Y0, x, Y0 + YH, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, x, Y0 - 10, fx(v), 7, FONT, GREY, 'middle')
    for v in yt:
        y = Y0 + (v - yt[0]) / (yt[-1] - yt[0]) * YH
        d.add(Line(X0, y, X0 + XW, y, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, X0 - 4, y - 2.5, fy(v), 7, FONT, GREY, 'end')
    d.add(Rect(X0, Y0, XW, YH, fillColor=None, strokeColor=colors.HexColor('#9fb0bf'),
               strokeWidth=0.8))
    _txt(d, X0 + XW / 2, Y0 - 22, xlab, 7.5, BOLD, DARK, 'middle')
    _txt(d, X0, Y0 + YH + 6, ylab, 7.5, BOLD, DARK)


def ca_tdc():
    """左：周期性 STOP 下的读数折叠关系；右：作者实测的单次标准差。"""
    d = Drawing(W, 262)
    # ---- 左：折叠 ----
    X0, Y0, XW, YH = 40, 54, 172, 168

    def lx(v):
        return X0 + v / 100 * XW

    def ly(v):
        return Y0 + v / 120 * YH

    d.add(Rect(lx(0), Y0, lx(12) - lx(0), YH, fillColor=colors.HexColor('#fbe3e0'),
               strokeColor=None))
    _axes(d, X0, Y0, XW, YH, list(range(0, 101, 20)), list(range(0, 121, 20)),
          '相位 phi：脉冲到下一个 10 MHz 沿 (ns)', 'TDC 读数 tau (ns)',
          lambda v: '%d' % v, lambda v: '%d' % v)
    for yv in (12, 112):
        _wire(d, [X0, ly(yv), X0 + XW, ly(yv)], GREY, 0.7, (3, 2))
    _wire(d, [lx(12), ly(12), lx(100), ly(100)], CLK, 1.8)
    _wire(d, [lx(0), ly(100), lx(12), ly(112)], PPS, 1.8)
    _txt(d, lx(14), ly(104), '折叠：读数 100 ~ 112 ns', 7, BOLD, PPS)
    _txt(d, lx(14), ly(94), '约 12% 的脉冲落在此区', 7, FONT, PPS)
    _txt(d, lx(46), ly(36), 'tau = phi', 7.5, BOLD, CLK)
    _txt(d, lx(1), ly(5), '死区', 7, BOLD, PPS)

    # ---- 右：实测标准差 ----
    X0, Y0, XW, YH = 296, 54, 178, 168

    def rx(v):
        return X0 + v / 1200 * XW

    def ry(v):
        return Y0 + v / 1100 * YH

    d.add(Rect(rx(12), Y0, rx(112) - rx(12), YH, fillColor=colors.HexColor('#dcebf7'),
               strokeColor=None))
    _axes(d, X0, Y0, XW, YH, list(range(0, 1201, 300)), list(range(0, 1101, 220)),
          '测量间隔 TOF (ns)', '单次标准差 (ps)', lambda v: '%d' % v, lambda v: '%d' % v)
    _wire(d, [rx(20), ry(0.87 * 20 - 18), rx(1200), ry(0.87 * 1200 - 18)], GREY, 0.7, (3, 2))
    for tof, sig in TDC_DATA:
        d.add(Circle(rx(tof), ry(sig), 1.7, fillColor=TDC, strokeColor=TDC))
    _txt(d, rx(130), ry(1010), '<- 工作区 12 ~ 112 ns', 7, BOLD, CLK)
    _txt(d, rx(130), ry(950), '   sigma 约 13 ~ 75 ps', 7, BOLD, CLK)
    _txt(d, rx(130), ry(870), '虚线：拟合斜率约 0.87 ps/ns', 7, FONT, GREY)

    _txt(d, 4, 6, '右图数据：作者 2022-08-28 实测，模式 1，CALIBRATION2 = 10 周期，每点 10 万次。'
         'STOP 先于或等于 START 时全部判为无效。', 7, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：调谐电压链路原理图

def ca_dac_sch():
    """按作者原理图重绘的调谐电压链路，元件值标注为 v1 / v2。"""
    d = Drawing(W, 222)
    g = Group()
    Y = 150

    # 分组虚线框
    for x, w, lab in ((4, 204, '调谐 DAC 与电压基准'), (211, 167, '二阶 Sallen-Key 有源低通'),
                      (382, 48, '无源 RC')):
        g.add(Rect(x, 96, w, 140, fillColor=None, strokeColor=colors.HexColor('#9aa8e0'),
                   strokeWidth=0.7, strokeDashArray=(3, 2)))
        _txt(g, x + 4, 228, lab, 7.5, BOLD, colors.HexColor('#3446a8'))

    # ADR4533
    _box(g, 12, 126, 50, 48, colors.HexColor('#fffbe6'), DARK, 0.9)
    _txt(g, 37, 160, 'ADR4533', 7.5, BOLD, DARK, 'middle')
    _txt(g, 37, 148, '3.300 V', 7, FONT, DARK, 'middle')
    _txt(g, 37, 136, 'U301', 6.5, FONT, GREY, 'middle')
    _wire(g, [37, 174, 37, 206])
    g.add(Rect(33, 186, 8, 7, fillColor=colors.HexColor('#c0392b'), strokeColor=None, rx=2, ry=2))
    _txt(g, 44, 187, 'JP301', 6.5, FONT, GREY)
    _txt(g, 44, 203, '+5 V（FB302）', 6.5, FONT, GREY)
    _wire(g, [37, 126, 37, 120])
    _gnd(g, 37, 120)

    # JP302 选择基准
    _wire(g, [62, Y, 80, Y])
    _box(g, 80, 142, 26, 16, colors.white, DARK, 0.9, r=2)
    _txt(g, 93, 147, 'JP302', 6.3, BOLD, DARK, 'middle')
    _wire(g, [106, Y, 140, Y])
    _dot(g, 120, Y)
    _cap(g, 120, Y, 120, 118)
    _gnd(g, 120, 118)
    _txt(g, 104, 112, '1u+100n', 6.3, FONT, GREY, 'end')
    _txt(g, 129, 154, 'VREF', 6.5, BOLD, DARK, 'middle')

    # AD5542A
    _box(g, 140, 118, 66, 64, colors.HexColor('#fffbe6'), DARK, 0.9)
    _txt(g, 173, 170, 'AD5542A', 7.5, BOLD, DARK, 'middle')
    _txt(g, 173, 160, '16 bit R-2R', 6.5, FONT, DARK, 'middle')
    _txt(g, 143, 146, 'REF', 6.3, FONT, GREY)
    _txt(g, 203, 146, 'VOUT', 6.3, FONT, GREY, 'end')
    _txt(g, 173, 133, '无缓冲输出', 6.3, FONT, RED, 'middle')
    _txt(g, 173, 124, '内阻约 6.25 k', 6.3, FONT, RED, 'middle')
    _wire(g, [173, 118, 173, 104], BUS, 0.9)
    _txt(g, 169, 102, 'SPI1 <- MCU', 6.5, FONT, BUS, 'end')

    # R311 / R312 / C313 / C314
    _wire(g, [206, Y, 214, Y])
    _res(g, 214, Y, 250, Y)
    _txt(g, 232, Y + 6, 'R311', 6.5, BOLD, DARK, 'middle')
    _txt(g, 232, Y - 12, '13k / 8k2', 6.5, FONT, ANA, 'middle')
    _wire(g, [250, Y, 254, Y])
    _dot(g, 254, Y)
    _res(g, 254, Y, 288, Y)
    _txt(g, 271, Y + 6, 'R312', 6.5, BOLD, DARK, 'middle')
    _txt(g, 271, Y - 12, '10k / 15k', 6.5, FONT, ANA, 'middle')
    _dot(g, 294, Y)
    _wire(g, [288, Y, 314, Y])
    _cap(g, 294, Y, 294, 118)
    _gnd(g, 294, 118)
    _txt(g, 286, 128, 'C314', 6.5, BOLD, DARK, 'end')
    _txt(g, 286, 120, '10u / 1u', 6.5, FONT, ANA, 'end')

    # 运放（同相端 Y，反相端 Y-17，输出 x=354）
    _tri(g, 314, Y - 8.5, 40, 34)
    _txt(g, 317, Y - 3, '+', 8, BOLD, DARK)
    _txt(g, 318, Y - 20, '-', 8, BOLD, DARK)
    _txt(g, 336, Y - 34, 'OPA189', 7, BOLD, DARK, 'middle')
    _wire(g, [330, Y + 1.7, 330, 176])
    _txt(g, 333, 172, '+5 V', 6.5, FONT, GREY)
    yo = Y - 8.5
    _wire(g, [354, yo, 372, yo])
    _dot(g, 366, yo)
    _wire(g, [366, yo, 366, 108, 306, 108, 306, Y - 17, 314, Y - 17])
    _wire(g, [254, Y, 254, 196, 302, 196])
    _cap(g, 302, 196, 314, 196)
    _wire(g, [314, 196, 366, 196, 366, yo])
    _txt(g, 308, 204, 'C313  20u / 2u2', 6.5, BOLD, DARK, 'middle')

    # R313 / C315
    _res(g, 372, yo, 410, yo)
    _txt(g, 391, yo + 6, 'R313', 6.5, BOLD, DARK, 'middle')
    _txt(g, 391, yo - 12, '100', 6.5, FONT, ANA, 'middle')
    _dot(g, 416, yo)
    _wire(g, [410, yo, 436, yo], ANA, 1.1)
    _cap(g, 416, yo, 416, 112)
    _gnd(g, 416, 112)
    _txt(g, 403, 122, '10u', 6.5, FONT, ANA, 'end')
    _txt(g, 419, yo + 4, 'VCTL', 6, BOLD, ANA)

    # OCXO
    _box(g, 436, 118, 42, 58, colors.HexColor('#eef4fb'), CLK, 1.0)
    _txt(g, 457, 160, 'OCXO', 7.5, BOLD, CLK, 'middle')
    _txt(g, 457, 149, 'AOCJY', 6.5, FONT, DARK, 'middle')
    _txt(g, 457, 125, 'OUT', 6.3, FONT, GREY, 'middle')
    _txt(g, 457, 104, '-> LMK1C1103', 6.5, FONT, CLK, 'middle')
    _wire(g, [457, 176, 457, 246, 93, 246, 93, 158], CLK, 0.9, (3, 2))
    _txt(g, 200, 249, 'OCXO_VREF：可改用 OCXO 自身基准，做比率式调谐', 6.8, FONT, CLK)

    notes = ['元件值格式：v1（2022-08-05，约 1 Hz）/ v2（2022-08-11，约 10 Hz）。R313 与 C315 两版相同。',
             'AD5542A 是无缓冲输出，约 6.25 k 内阻与 R311 串联，会把实际截止频率拉低约 20%，见第 5.2 节。',
             'OPA189 由 +5 V 单电源供电；同相端共模上限约 V+ - 2.5 V = 2.5 V，见第 5.4 节。']
    for i, s in enumerate(notes):
        _txt(g, 4, 76 - i * 14, s, 7, FONT, DARK)
    g.translate(0, -40)
    d.add(g)
    return d


# ---------------------------------------------------------------- 图：滤波器幅频响应

def _sk_out(f, R1, R2, C1, C2, Ro=8.0, gbw=14e6):
    """单位增益 Sallen-Key 低通（运放取有限增益带宽积与输出电阻 Ro，负载为 R313/C315）。
    返回 (有源级输出, 经 R313/C315 后的 VCTL)，输入为 1 V。"""
    s = 2j * math.pi * f
    A = 2 * math.pi * gbw / s
    yl = 1 / (100 + 1 / (s * 10e-6))
    a = [[1 / R1 + 1 / R2 + s * C1, -1 / R2, -s * C1],
         [-1 / R2, 1 / R2 + s * C2, 0],
         [-s * C1, -A / Ro, (1 + A) / Ro + s * C1 + yl]]
    b = [1 / R1, 0, 0]

    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    vo = det([[a[i][0], a[i][1], b[i]] for i in range(3)]) / det(a)
    return vo, vo / (1 + s * 100 * 10e-6)


def ca_lpf_bode():
    """两版调谐滤波器的幅频响应（按原理图元件值计算）。"""
    d = Drawing(W, 286)
    X0, Y0, XW, YH = 54, 74, 404, 182
    FL, FH, DL, DH = -1, 6, -180, 0

    def px(f):
        return X0 + (math.log10(f) - FL) / (FH - FL) * XW

    def py(db):
        return Y0 + (max(db, DL) - DL) / (DH - DL) * YH

    for e in range(FL, FH + 1):
        x = px(10.0 ** e)
        d.add(Line(x, Y0, x, Y0 + YH, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, x, Y0 - 10, {-1: '0.1', 0: '1', 1: '10', 2: '100', 3: '1k', 4: '10k',
                             5: '100k', 6: '1M'}[e], 7, FONT, GREY, 'middle')
    for db in range(DL, DH + 1, 30):
        y = py(db)
        d.add(Line(X0, y, X0 + XW, y, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, X0 - 4, y - 2.5, '%d' % db, 7, FONT, GREY, 'end')
    d.add(Rect(X0, Y0, XW, YH, fillColor=None, strokeColor=colors.HexColor('#9fb0bf'),
               strokeWidth=0.8))
    _txt(d, X0 + XW / 2, Y0 - 22, '频率 (Hz)', 7.5, BOLD, DARK, 'middle')
    _txt(d, X0 - 40, Y0 + YH + 6, '增益 (dB)', 7.5, BOLD, DARK)

    xr = px(159.15)
    _wire(d, [xr, Y0, xr, Y0 + YH], GREY, 0.6, (1.5, 2))
    _txt(d, xr + 3, Y0 + YH - 10, 'RC 极点 159 Hz', 6.8, FONT, GREY)

    vers = [('v1', 13e3, 10e3, 20e-6, 10e-6, ANA), ('v2', 8.2e3, 15e3, 2.2e-6, 1e-6, CLK)]
    fs = [10 ** (FL + i * (FH - FL) / 280) for i in range(281)]
    for name, R1, R2, C1, C2, col in vers:
        act, tot = [], []
        for f in fs:
            a, t = _sk_out(f, R1, R2, C1, C2)
            act.append(20 * math.log10(abs(a)))
            tot.append(20 * math.log10(abs(t)))
        _wire(d, sum(([px(f), py(v)] for f, v in zip(fs, act)), []), col, 0.8, (3, 2))
        _wire(d, sum(([px(f), py(v)] for f, v in zip(fs, tot)), []), col, 1.8)
        # -3 dB 点（对分法细化）与有源级的斜率反转点
        lo = max(f for f, v in zip(fs, tot) if v >= -3)
        hi = lo * 10 ** ((FH - FL) / 280)
        for _ in range(40):
            mid = math.sqrt(lo * hi)
            if 20 * math.log10(abs(_sk_out(mid, R1, R2, C1, C2)[1])) >= -3:
                lo = mid
            else:
                hi = mid
        f3 = lo
        d.add(Circle(px(f3), py(-3), 2.4, fillColor=colors.white, strokeColor=col,
                     strokeWidth=1.2))
        i_min = min(range(len(fs)), key=lambda i: act[i])
        fm = fs[i_min]
        d.add(Circle(px(fm), py(act[i_min]), 2.4, fillColor=col, strokeColor=col))
        _txt(d, X0 + XW - 6, py(-60 if name == 'v1' else -45),
             '%s 有源级斜率反转 %.1f kHz（实心点）' % (name, fm / 1e3), 7, BOLD, col, 'end')
        _txt(d, X0 + 6, py(-120 if name == 'v1' else -135),
             '%s：-3 dB 点 %.2f Hz（空心圈）' % (name, f3), 7, BOLD, col)

    ly = 30
    for i, (c, dash, t) in enumerate(((ANA, None, 'v1 总响应（至 VCTL）'),
                                      (ANA, (3, 2), 'v1 仅有源级'),
                                      (CLK, None, 'v2 总响应（至 VCTL）'),
                                      (CLK, (3, 2), 'v2 仅有源级'))):
        bx = 8 + i * 118
        ln = Line(bx, ly + 3, bx + 18, ly + 3, strokeColor=c, strokeWidth=1.6 if not dash else 0.9)
        if dash:
            ln.strokeDashArray = dash
        d.add(ln)
        _txt(d, bx + 22, ly, t, 7, FONT, DARK)
    _txt(d, 8, 12, '按原理图元件值计算；运放取 GBW 14 MHz，等效输出电阻 8 欧（使反转频率与作者 PSpice 结论一致）。'
         '未计 DAC 内阻。', 7, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：调谐分辨率

def ca_tuning():
    """DAC 一个 LSB 的频率步进在 tau 秒内累积出的时间误差。"""
    d = Drawing(W, 250)
    X0, Y0, XW, YH = 60, 62, 392, 166
    TL, TH, EL, EH = 0, 3, -12, -7               # 1 s..1000 s；1 ps..100 ns

    def px(t):
        return X0 + (math.log10(t) - TL) / (TH - TL) * XW

    def py(e):
        return Y0 + (math.log10(e) - EL) / (EH - EL) * YH

    for e in range(TL, TH + 1):
        x = px(10 ** e)
        d.add(Line(x, Y0, x, Y0 + YH, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, x, Y0 - 10, ('1 s', '10 s', '100 s', '1000 s')[e], 7, FONT, GREY, 'middle')
    for e in range(EL, EH + 1):
        y = py(10.0 ** e)
        d.add(Line(X0, y, X0 + XW, y, strokeColor=LIGHT, strokeWidth=0.5))
        _txt(d, X0 - 4, y - 2.5, {-12: '1 ps', -11: '10 ps', -10: '100 ps',
                                  -9: '1 ns', -8: '10 ns', -7: '100 ns'}[e], 7, FONT, GREY, 'end')
    d.add(Rect(X0, Y0, XW, YH, fillColor=None, strokeColor=colors.HexColor('#9fb0bf'),
               strokeWidth=0.8))
    _txt(d, X0 + XW / 2, Y0 - 22, '持续时间 tau', 7.5, BOLD, DARK, 'middle')
    _txt(d, X0 - 50, Y0 + YH + 6, '1 LSB 累积的时间误差', 7.5, BOLD, DARK)

    _wire(d, [X0, py(50e-12), X0 + XW, py(50e-12)], TDC, 1.0, (4, 2))
    _txt(d, X0 + XW - 4, py(50e-12) + 3, 'TDC7200 单次约 50 ps', 7, BOLD, TDC, 'end')
    _wire(d, [X0, py(1e-9), X0 + XW, py(1e-9)], RED, 1.0, (4, 2))
    _txt(d, X0 + 4, py(1e-9) + 3, '作者期望的 1 ns', 7, BOLD, RED)

    lines = ((16, ANA, 1.8), (20, CLK, 1.4))
    for bits, col, sw in lines:
        step = 2e-6 / 2 ** bits                    # 2 ppm 调谐范围
        _wire(d, [px(1), py(step), px(1000), py(step * 1000)], col, sw)

    d.add(Circle(px(10), py(305e-12), 3, fillColor=RED, strokeColor=RED))
    _txt(d, px(10) + 6, py(305e-12) - 12, '作者算例 305 ps', 7, BOLD, RED)

    for i, (bits, col, sw) in enumerate(lines):
        bx = 8 + i * 170
        d.add(Line(bx, 27, bx + 18, 27, strokeColor=col, strokeWidth=sw))
        _txt(d, bx + 22, 24, '%d bit DAC：%.3g ppt / LSB' % (bits, 2e-6 / 2 ** bits * 1e12),
             7, BOLD, col)
    _txt(d, 8, 9, '假设 OCXO 调谐范围 2 ppm 全部落在 DAC 满量程内。斜线是 1 LSB 频率步进在 tau 内累积的时间误差。',
         7, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：控制环信号流

def ca_loop():
    """数字锁相环的信号流（按帖子描述整理，作者未公开固件）。"""
    d = Drawing(W, 292)
    _blk(d, 4, 196, 82, 44, 'ZED-F9T', ['TP1 脉冲', 'TIM-TP 含 qErr'], PPS)
    _blk(d, 108, 196, 86, 44, '两级 TIC', ['TIM2 粗测', 'TDC7200 细测'], TDC)
    d.add(Circle(222, 218, 11, fillColor=colors.white, strokeColor=DARK, strokeWidth=1))
    _txt(d, 222, 215, '+', 9, BOLD, DARK, 'middle')
    _blk(d, 250, 196, 98, 44, '锯齿修正', ['减去 qErr', '得时间误差 x(n)'], PPS)
    _blk(d, 372, 196, 106, 44, '数字 PI 控制器', ['时间常数远大于', '滤波器群时延'], MCU_C)
    _box(d, 372, 254, 106, 26, colors.white, SEN, 0.9, r=3)
    _txt(d, 425, 269, 'TMP117 温度 / IMU 加速度', 6.8, BOLD, SEN, 'middle')
    _txt(d, 425, 259, '前馈补偿（v2 加 IMU，待实现）', 6.5, FONT, SEN, 'middle')
    _arrow(d, 425, 254, 425, 241, SEN, 0.9)

    _blk(d, 372, 118, 106, 44, '16 bit DAC', ['AD5542A', '可加 PWM 抖动扩位'], ANA)
    _blk(d, 372, 40, 106, 44, '有源低通', ['群时延 v1 0.23 s', 'v2 0.024 s'], ANA)
    _blk(d, 250, 40, 98, 44, '被控 OCXO', ['VCTL -> 频率', '低 g 敏感型（规划）'], CLK)
    _blk(d, 128, 40, 80, 44, '时钟分配', ['LMK1C1103', '3 路同相'], CLK)
    _blk(d, 176, 118, 92, 40, '本地脉冲生成', ['TIM2 / HRTIM', '同时驱动脉冲输出'], MCU_C)

    _arrow(d, 86, 218, 107, 218, PPS, 1.1)
    _arrow(d, 194, 218, 210, 218, TDC, 1.1)
    _arrow(d, 233, 218, 249, 218, DARK, 1.1)
    _arrow(d, 348, 218, 371, 218, PPS, 1.1)
    _arrow(d, 425, 196, 425, 163, MCU_C, 1.1)
    _txt(d, 429, 177, 'DAC 码', 6.5, BOLD, MCU_C)
    _arrow(d, 425, 118, 425, 85, ANA, 1.1)
    _arrow(d, 372, 62, 349, 62, ANA, 1.2)
    _txt(d, 360, 66, 'VCTL', 6.3, BOLD, ANA, 'middle')
    _arrow(d, 250, 62, 209, 62, CLK, 1.2)
    _txt(d, 229, 66, '10 MHz', 6.5, BOLD, CLK, 'middle')
    # LMK -> 本地脉冲生成、LMK -> TIC
    _wire(d, [184, 84, 184, 100, 222, 100], CLK, 1.1)
    _arrow(d, 222, 100, 222, 117, CLK, 1.1)
    _arrow(d, 222, 158, 222, 206, MCU_C, 1.1)
    _txt(d, 226, 176, 't_local（-）', 6.5, BOLD, MCU_C)
    _arrow(d, 150, 84, 150, 195, CLK, 1.1)
    # 对外输出
    _arrow(d, 128, 62, 92, 62, CLK, 1.2)
    _txt(d, 6, 59, '10 MHz 输出', 7, BOLD, CLK)
    # RTCM 输入
    _arrow(d, 45, 270, 45, 241, GREEN, 1.0)
    _txt(d, 50, 262, 'RTCM 3 差分修正', 7, BOLD, GREEN)

    _txt(d, 4, 20, '作者未公开固件。本图按帖子中的描述整理：qErr 修正、群时延补偿、IMU 前馈均为推断或规划项。',
         7, FONT, GREY)
    _txt(d, 4, 7, '环路的所有比较都在 OCXO 相干时钟域内完成，只有 GNSS 脉冲是外部异步输入。', 7, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：输出驱动

def ca_output():
    """BUF602 输出级：源端 49.9 欧匹配，可驱动 50 欧或高阻负载。"""
    d = Drawing(W, 236)
    Y = 160
    _txt(d, 4, 226, 'BUF602 输出级（5 路相同）', 8.5, BOLD, DARK)
    _txt(d, 6, Y + 6, 'CMOS 3.3 V', 7, BOLD, DARK)
    _txt(d, 6, Y - 8, '来自 LMK / MCU / F9T', 6.5, FONT, GREY)
    _arrow(d, 64, Y, 86, Y, DARK, 0.9)
    _tri(d, 86, Y, 42, 40)
    _txt(d, 101, Y - 3, 'BUF', 7, BOLD, DARK, 'middle')
    _wire(d, [104, Y + 11.4, 104, 196])
    _txt(d, 108, 192, '+5 V', 6.5, FONT, GREY)
    _wire(d, [104, Y - 11.4, 104, 124])
    _txt(d, 108, 124, '-5 V', 6.5, FONT, GREY)
    _res(d, 128, Y, 172, Y)
    _txt(d, 150, Y + 6, '49.9 欧', 6.8, BOLD, DARK, 'middle')
    _dot(d, 182, Y)
    _wire(d, [172, Y, 200, Y])
    # TVS（双向）
    _wire(d, [182, Y, 182, Y - 12])
    cy = Y - 20
    d.add(Polygon([176, cy + 8, 188, cy + 8, 182, cy], fillColor=DARK, strokeColor=DARK))
    d.add(Polygon([176, cy - 8, 188, cy - 8, 182, cy], fillColor=DARK, strokeColor=DARK))
    d.add(Line(176, cy, 188, cy, strokeColor=DARK, strokeWidth=1))
    _wire(d, [182, cy - 8, 182, cy - 16])
    _gnd(d, 182, cy - 16)
    _txt(d, 192, cy - 3, 'TVS', 6.5, FONT, GREY)
    _sma(d, 206, Y)
    _txt(d, 206, Y + 10, 'SMA', 6.5, FONT, GREY, 'middle')
    for dy in (-4, 4):
        _wire(d, [212, Y + dy, 296, Y + dy], GREY, 0.9)
    _txt(d, 254, Y + 8, '50 欧同轴', 6.8, FONT, GREY, 'middle')
    _wire(d, [296, Y, 312, Y + 30], GREY, 0.8, (2, 2))
    _wire(d, [296, Y, 312, Y - 30], GREY, 0.8, (2, 2))

    def load(y, title, line2, amp):
        _box(d, 314, y - 18, 164, 36, colors.white, ACCENT, 0.9, r=3)
        _txt(d, 320, y + 6, title, 7, BOLD, DARK)
        _txt(d, 320, y - 6, line2, 6.6, FONT, GREY)
        h = 12 * amp / 3.3
        bx0 = 434
        _wire(d, [bx0, y - 8, bx0 + 8, y - 8, bx0 + 8, y - 8 + h, bx0 + 22, y - 8 + h,
                  bx0 + 22, y - 8, bx0 + 34, y - 8], ACCENT, 1.1)
        _txt(d, bx0 + 17, y + 8, '%.2f V' % amp, 6.5, BOLD, ACCENT, 'middle')

    load(Y + 30, '50 欧负载', '与源端 49.9 欧分压', 1.65)
    load(Y - 30, '高阻负载', '末端全反射，源端吸收反射波', 3.3)

    chans = [('J401', '10 MHz', 'LMK Y0', CLK), ('J411', '10 MHz', 'LMK Y0', CLK),
             ('J441', '稳定脉冲', 'MCU PA9', PPS), ('J451', '稳定脉冲', 'MCU PA9', PPS),
             ('J491', 'F9T TP2', '接收机直出', PPS)]
    for i, (ref, name, src, col) in enumerate(chans):
        x = 4 + i * 95
        _box(d, x, 46, 88, 40, colors.white, col, 1.0, r=3)
        _txt(d, x + 44, 72, '%s  %s' % (ref, name), 7.3, BOLD, col, 'middle')
        _txt(d, x + 44, 56, '来源：%s' % src, 6.8, FONT, GREY, 'middle')
    _txt(d, 4, 26, 'BUF602 压摆率 8 V/ns，上升沿 < 0.5 ns，PSRR > 45 dB（至 1 MHz），以上为作者引用的数据手册值。',
         7, FONT, DARK)
    _txt(d, 4, 12, '+/-5 V 与 +3.3 V 全部由 J101 端子从外部供入，板上没有稳压器。', 7, FONT, DARK)
    return d


# ---------------------------------------------------------------- 图：MCU 引脚分配

def ca_pinmap():
    """STM32G474RET6 在 v2 原理图中的引脚分配。"""
    d = Drawing(W, 300)
    cx0, cx1, cy0, cy1 = 160, 322, 30, 282
    _box(d, cx0, cy0, cx1 - cx0, cy1 - cy0, colors.HexColor('#f4f6f8'), MCU_C, 1.2, r=4)
    mx = (cx0 + cx1) / 2
    _txt(d, mx, 160, 'STM32G474RET6', 8.5, BOLD, MCU_C, 'middle')
    _txt(d, mx, 148, 'LQFP64，170 MHz', 7, FONT, GREY, 'middle')
    _txt(d, mx, 136, '时钟取自 OCXO', 7, FONT, GREY, 'middle')

    left = [('PF0', '5', '10MHZ_MCU（HSE 旁路）', CLK),
            ('PB11', '33', 'PULSE_GNSS（TIM2_CH4）', PPS),
            ('PC10', '52', 'UART4_TX -> F9T RXD', BUS),
            ('PC11', '53', 'UART4_RX <- F9T TXD', BUS),
            ('PC8', '40', 'I2C3_SCL -> TMP117', SEN),
            ('PC9', '41', 'I2C3_SDA <-> TMP117', SEN),
            ('PA11', '45', 'USB D-', BUS),
            ('PA12', '46', 'USB D+', BUS),
            ('PA13', '49', 'SWDIO', GREY),
            ('PA14', '50', 'SWCLK', GREY),
            ('PA0~2', '12~14', 'LED 绿 / 黄 / 红', GREY)]
    right = [('PA9', '43', 'PULSE_MCU（TIM2_CH3）', PPS),
             ('PA4', '18', 'SPI1_NSS -> DAC', ANA),
             ('PA5', '19', 'SPI1_SCK -> DAC', ANA),
             ('PA7', '21', 'SPI1_MOSI -> DAC', ANA),
             ('PB12', '34', 'SPI2_NSS -> TDC', TDC),
             ('PB13', '35', 'SPI2_SCK -> TDC', TDC),
             ('PB14', '36', 'SPI2_MISO <- TDC', TDC),
             ('PB15', '37', 'SPI2_MOSI -> TDC', TDC),
             ('PC6', '38', 'TDC INTB（4k7 上拉）', TDC),
             ('PC7', '39', 'TDC ENABLE', TDC),
             ('PA15', '51', 'SPI3_NSS -> IMU', SEN),
             ('PB3~5', '56~58', 'SPI3 <-> IMU', SEN),
             ('PB6', '59', 'TIM4_CH1 -> IMU CLKIN', SEN)]
    for i, (pin, num, net, col) in enumerate(left):
        y = 268 - i * 21
        d.add(Line(cx0 - 12, y, cx0, y, strokeColor=col, strokeWidth=1.4))
        _txt(d, cx0 + 4, y - 2.5, '%s · %s' % (pin, num), 6.8, BOLD, col)
        _txt(d, cx0 - 16, y - 2.5, net, 7, FONT, DARK, 'end')
    for i, (pin, num, net, col) in enumerate(right):
        y = 270 - i * 18.5
        d.add(Line(cx1, y, cx1 + 12, y, strokeColor=col, strokeWidth=1.4))
        _txt(d, cx1 - 4, y - 2.5, '%s · %s' % (pin, num), 6.8, BOLD, col, 'end')
        _txt(d, cx1 + 16, y - 2.5, net, 7, FONT, DARK)
    for i, s in enumerate(('PA9 也可作', 'HRTIM1_CHA2', '184 ps 输出')):
        _txt(d, mx, 112 - i * 10, s, 6.8, BOLD if i == 1 else FONT, PPS, 'middle')
    _txt(d, 4, 12, 'v1（08-05）差异：TDC ENABLE / INTB 在 PC8 / PC9，TMP117 走 I2C4（PC6 / PC7），无 IMU 与 LED。',
         7, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：PCB 布局

def ca_board():
    """v2 版图（100 x 100 mm）的器件分区，按作者版图 PDF 量取，示意。"""
    d = Drawing(W, 300)
    K, BX, BT = 2.6, 16, 288                       # mm -> pt；板左边与上边

    def r(x, y, w, h, fill, stroke, lab='', sub='', sw=0.9, dash=None, fs=6.8):
        rect = Rect(BX + x * K, BT - (y + h) * K, w * K, h * K, fillColor=fill,
                    strokeColor=stroke, strokeWidth=sw)
        if dash:
            rect.strokeDashArray = dash
        d.add(rect)
        cxp, cyp = BX + (x + w / 2) * K, BT - (y + h / 2) * K
        if lab:
            _txt(d, cxp, cyp + (1 if sub else -2.5), lab, fs, BOLD, DARK, 'middle')
        if sub:
            _txt(d, cxp, cyp - 8, sub, 6.2, FONT, GREY, 'middle')

    r(0, 0, 100, 100, colors.HexColor('#eef3ea'), colors.HexColor('#5d7a52'), sw=1.4)
    for hx, hy in ((4, 4), (96, 4), (4, 96), (96, 96)):
        d.add(Circle(BX + hx * K, BT - hy * K, 4, fillColor=colors.white,
                     strokeColor=GREY, strokeWidth=0.8))
    r(13.5, 0.5, 22.5, 11, colors.white, DARK, 'J101 电源端子', '-5V GND 3V3 5V')
    r(41, 1, 11, 11, colors.white, GREY, 'SWD')
    r(2, 23, 40, 40, colors.HexColor('#fde8f6'), colors.HexColor('#d63384'), sw=1.6)
    _txt(d, BX + 22 * K, BT - 61 * K, 'Hammond 1551P 塑料罩', 6.5, BOLD,
         colors.HexColor('#d63384'), 'middle')
    r(7, 30, 29, 26, colors.white, CLK, 'OCXO', 'Abracon AOCJY')
    r(4, 24.5, 10, 4.5, colors.white, SEN, 'TMP117', fs=5.6)
    r(44, 23, 19.5, 18.5, colors.white, SEN, 'IMU 子板', 'IIM-42652')
    r(66, 0.5, 32, 68, colors.HexColor('#fff4e5'), PPS, sw=1.2, dash=(4, 2))
    _txt(d, BX + 82 * K, BT - 18 * K, 'RCB-F9T 子板', 6.8, BOLD, PPS, 'middle')
    _txt(d, BX + 82 * K, BT - 22 * K, '叠插区域', 6.5, FONT, PPS, 'middle')
    r(74, 0.5, 7, 9, colors.white, PPS, '天线', fs=5.8)
    r(83, 0.5, 9, 5, colors.white, BUS, 'USB', fs=5.8)
    r(72, 34, 15, 15, colors.white, MCU_C, 'STM32', 'G474RE')
    r(70, 52, 8, 8, colors.white, TDC, 'TDC', fs=6)
    r(82, 59, 9, 5, colors.white, PPS, 'J102', fs=5.8)
    r(46, 44, 14, 9, colors.white, ANA, 'OPA189', fs=6)
    r(50.5, 56, 9, 5.5, colors.white, ANA, 'DAC', fs=6)
    r(43, 62, 6, 7, colors.white, ANA, '基准', fs=5.6)
    r(19, 67, 10, 7, colors.white, CLK, 'LMK', fs=6)
    r(67, 70, 9, 5, colors.white, GREY, 'LED', fs=5.6)
    r(5, 77, 92, 12, colors.HexColor('#f4f6f8'), DARK, 'BUF602 x5 输出驱动')
    for i, (sx, lab, col) in enumerate(((10, '10M', CLK), (30, '10M', CLK), (50, 'PPS', PPS),
                                        (70, 'PPS', PPS), (90, 'TP2', PPS))):
        d.add(Rect(BX + (sx - 4) * K, BT - 100 * K - 8, 8 * K, 12, fillColor=colors.white,
                   strokeColor=col, strokeWidth=1))
        _txt(d, BX + sx * K, BT - 100 * K - 5, lab, 6, BOLD, col, 'middle')
    _txt(d, BX + 50 * K, BT + 3, '100 mm', 7, BOLD, GREY, 'middle')

    notes = ['板框 100 x 100 mm（含 SMA 底座），可装入常见铝壳',
             'OCXO 在左上，塑料罩挡气流；TMP117 放在罩内',
             'RCB-F9T 用 2x4 排针 J102 叠插在右上方',
             'MCU 与 TDC7200 紧挨，位于 RCB-F9T 下方',
             '基准、DAC、有源滤波夹在 OCXO 罩与 MCU 之间',
             'LMK1C1103 紧贴 OCXO 输出脚',
             '5 路 SMA 全部排在下沿',
             '无板载稳压器，三路电源由 J101 外供',
             'IMU 子板位于板中央（v2 新增）']
    for i, s in enumerate(notes):
        _txt(d, 300, 270 - i * 17, '- ' + s, 7, FONT, DARK)
    return d


FIGURES = {
    'flow': flow,
    'stackup': stackup,
    'microstrip': microstrip,
    'priority': priority,
    'refplane': refplane,
    'layout': layout,
    'sch_flow': sch_flow,
    'sch_connect': sch_connect,
    'sch_hierarchy': sch_hierarchy,
    'sch_dataflow': sch_dataflow,
    'sch_erc': sch_erc,
    'ocxo_pinout': ocxo_pinout,
    'ocxo_chain': ocxo_chain,
    'gnss_size': gnss_size,
    'gnss_chain': gnss_chain,
    'gpsdo_adev': gpsdo_adev,
    'gpsdo_tic': gpsdo_tic,
    'gpsdo_res_bar': gpsdo_res_bar,
    'v11_roadmap': v11_roadmap,
    'ca_usecase': ca_usecase,
    'ca_system': ca_system,
    'ca_clock_tree': ca_clock_tree,
    'ca_tic_timing': ca_tic_timing,
    'ca_tdc': ca_tdc,
    'ca_dac_sch': ca_dac_sch,
    'ca_lpf_bode': ca_lpf_bode,
    'ca_tuning': ca_tuning,
    'ca_loop': ca_loop,
    'ca_output': ca_output,
    'ca_pinmap': ca_pinmap,
    'ca_board': ca_board,
}


def make(name, caption=''):
    """返回可插入 story 的 flowable 列表。"""
    if name not in FIGURES:
        raise SystemExit('[ERROR] 未定义的插图: %s（可用: %s）'
                         % (name, ', '.join(sorted(FIGURES))))
    out = [Spacer(1, 4), FIGURES[name]()]
    if caption:
        out.append(Paragraph(caption, CAP))
    else:
        out.append(Spacer(1, 8))
    return out
