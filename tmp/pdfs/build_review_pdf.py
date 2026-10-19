from pathlib import Path
from xml.sax.saxutils import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, HRFlowable


ROOT = Path(r"G:/C++/GPSDO-master")
SOURCE = ROOT / "docs/hardware/原理图电路复核_2026-10-19.md"
OUTPUT = ROOT / "output/pdf/原理图电路复核_2026-10-19.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont("SimHei", r"C:/Windows/Fonts/simhei.ttf"))
ink = colors.HexColor("#17243a")
blue = colors.HexColor("#19589b")
muted = colors.HexColor("#617085")

styles = {
    "title": ParagraphStyle("title", fontName="SimHei", fontSize=20, leading=27,
                            textColor=ink, spaceAfter=14),
    "intro": ParagraphStyle("intro", fontName="SimHei", fontSize=9, leading=15,
                            textColor=muted, spaceAfter=15),
    "h2": ParagraphStyle("h2", fontName="SimHei", fontSize=13.5, leading=20,
                         textColor=blue, spaceBefore=15, spaceAfter=7, keepWithNext=True),
    "h3": ParagraphStyle("h3", fontName="SimHei", fontSize=10.7, leading=17,
                         textColor=ink, spaceBefore=11, spaceAfter=5, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="SimHei", fontSize=9.2, leading=16.2,
                           textColor=ink, spaceAfter=7, wordWrap="CJK", allowWidows=0,
                           allowOrphans=0, alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="SimHei", fontSize=9.2, leading=16.2,
                             textColor=ink, leftIndent=13, firstLineIndent=-10,
                             spaceAfter=5, wordWrap="CJK"),
    "source": ParagraphStyle("source", fontName="SimHei", fontSize=8.6, leading=14,
                             textColor=ink, leftIndent=13, firstLineIndent=-10,
                             spaceAfter=4, wordWrap="CJK"),
}

def markup(line):
    result = escape(line.replace("µ", "u"))
    result = re.sub(r"(https?://[^\s<]+)",
                    lambda m: f'<link href="{m.group(1)}" color="#19589b">{m.group(1)}</link>',
                    result)
    return result


def footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#d9e1ea"))
    canvas.line(45, 40, width - 45, 40)
    canvas.setFont("SimHei", 8)
    canvas.setFillColor(muted)
    canvas.drawString(45, 27, "GPSDO Rev1.0  |  原理图电路复核  |  2026-10-19")
    canvas.drawRightString(width - 45, 27, f"{doc.page}")
    canvas.restoreState()


lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
story = []
for i, raw in enumerate(lines):
    line = raw.strip()
    if not line:
        continue
    if line.startswith("# "):
        story.append(Paragraph(markup(line[2:]), styles["title"]))
        story.append(HRFlowable(width="100%", thickness=1.3, color=blue, spaceAfter=11))
    elif i == 2 and line.startswith("检查时间"):
        story.append(Paragraph(markup(line), styles["intro"]))
    elif line.startswith("## "):
        story.append(Paragraph(markup(line[3:]), styles["h2"]))
    elif line.startswith("### "):
        story.append(Paragraph(markup(line[4:]), styles["h3"]))
    elif line.startswith("- "):
        style = styles["source"] if "https://" in line else styles["bullet"]
        story.append(Paragraph("- " + markup(line[2:]), style))
    else:
        story.append(Paragraph(markup(line), styles["body"]))

doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=45, rightMargin=45,
                        topMargin=43, bottomMargin=54,
                        title="GPSDO 原理图电路复核", author="Codex")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
