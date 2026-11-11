from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


def main() -> None:
    directory = Path(__file__).resolve().parent
    title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=colors.HexColor("#185c70"), spaceAfter=22)
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=16, leading=23, spaceAfter=16)
    story = []
    for line in (directory / "presentation.md").read_text().splitlines():
        if line.startswith("# "):
            if story:
                story.append(PageBreak())
            story.append(Paragraph(escape(line[2:]), title))
        elif line.startswith("!["):
            path = str(directory / line.split("(", 1)[1].rstrip(")"))
            width, height = ImageReader(path).getSize()
            scale = min(860 / width, 380 / height)
            story.append(Image(path, width=width * scale, height=height * scale))
        elif line.strip():
            story.append(Paragraph(escape(line), body))
        else:
            story.append(Spacer(1, 2))
    document = SimpleDocTemplate(str(directory / "presentation.pdf"), pagesize=(960, 600), leftMargin=48, rightMargin=48, topMargin=36, bottomMargin=32, title="Estación meteorológica IoT", author="Esteban Cárcamo y Felipe Aguilar")
    document.build(story)


if __name__ == "__main__":
    main()
