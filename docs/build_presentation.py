from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

PAGE_SIZE = (960, 600)
ACCENT = colors.HexColor("#185c70")
MUTED = colors.HexColor("#5b6b73")
QUESTION_BACKGROUND = colors.HexColor("#e8f1f4")
FOOTER = "CC3067 Redes · Estación meteorológica IoT · Esteban Cárcamo y Felipe Aguilar"


def draw_frame(canvas, document) -> None:
    width, height = PAGE_SIZE
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, height - 10, width, 10, stroke=0, fill=1)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 10)
    canvas.drawString(48, 16, FOOTER)
    canvas.drawRightString(width - 48, 16, str(document.page))
    canvas.restoreState()


def draw_cover(canvas, document) -> None:
    width, height = PAGE_SIZE
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, 0, 24, height, stroke=0, fill=1)
    canvas.restoreState()


def main() -> None:
    directory = Path(__file__).resolve().parent
    cover = ParagraphStyle("Cover", fontName="Helvetica-Bold", fontSize=44, leading=52, textColor=ACCENT, spaceAfter=28)
    title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=ACCENT, spaceAfter=18)
    question = ParagraphStyle("Question", fontName="Helvetica-Bold", fontSize=16, leading=21, textColor=ACCENT, backColor=QUESTION_BACKGROUND, borderPadding=(8, 10, 8, 10), spaceBefore=6, spaceAfter=16)
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=15, leading=21, spaceAfter=11)
    caption = ParagraphStyle("Caption", parent=body, fontSize=13, leading=18, textColor=MUTED, spaceAfter=10)
    slides = [chunk.splitlines() for chunk in ("\n" + (directory / "presentation.md").read_text()).split("\n# ")[1:]]
    story = []
    for index, (heading, *lines) in enumerate(slides):
        story.append(PageBreak() if index else Spacer(1, 120))
        story.append(Paragraph(escape(heading), title if index else cover))
        text_style = caption if any(line.startswith("![") for line in lines) else body
        for line in lines:
            if line.startswith("## "):
                story.append(Paragraph(escape(line[3:]), question))
            elif line.startswith("!["):
                path = str(directory / line.split("(", 1)[1].rstrip(")"))
                width, height = ImageReader(path).getSize()
                scale = min(860 / width, 400 / height)
                story.append(Image(path, width=width * scale, height=height * scale))
            elif line.strip():
                story.append(Paragraph(escape(line), text_style))
            else:
                story.append(Spacer(1, 2))
    document = SimpleDocTemplate(str(directory / "presentation.pdf"), pagesize=PAGE_SIZE, leftMargin=48, rightMargin=48, topMargin=36, bottomMargin=40, title="Estación meteorológica IoT", author="Esteban Cárcamo y Felipe Aguilar")
    document.build(story, onFirstPage=draw_cover, onLaterPages=draw_frame)


if __name__ == "__main__":
    main()
