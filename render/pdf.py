from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

PAGE = A4
MARGIN_LEFT = 0.65 * inch
MARGIN_RIGHT = 0.65 * inch
MARGIN_TOP = 0.55 * inch
MARGIN_BOTTOM = 0.60 * inch

DARK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
RULE = colors.HexColor("#888888")


def styles():
    return {
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=20, leading=24,
            alignment=TA_CENTER, textColor=DARK, spaceAfter=2,
        ),
        "role": ParagraphStyle(
            "role", fontName="Helvetica", fontSize=11, leading=15,
            alignment=TA_CENTER, textColor=GREY, spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "contact", fontName="Helvetica", fontSize=9.5, leading=13,
            alignment=TA_CENTER, textColor=GREY, spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=DARK, spaceBefore=7, spaceAfter=1,
        ),
        "item_header_left": ParagraphStyle(
            "item_header_left", fontName="Helvetica", fontSize=10.5, leading=13,
            textColor=DARK, alignment=0,
        ),
        "item_header_right": ParagraphStyle(
            "item_header_right", fontName="Helvetica", fontSize=10, leading=13,
            textColor=GREY, alignment=TA_RIGHT,
        ),
        "project_tech": ParagraphStyle(
            "project_tech", fontName="Helvetica-Oblique", fontSize=9.5, leading=12,
            textColor=GREY, spaceAfter=1,
        ),
        "detail_line": ParagraphStyle(
            "detail_line", fontName="Helvetica", fontSize=10, leading=13,
            textColor=GREY, spaceAfter=1,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=10, leading=13.2,
            textColor=DARK, leftIndent=14, bulletIndent=2, spaceAfter=1.5,
        ),
        "skills_line": ParagraphStyle(
            "skills_line", fontName="Helvetica", fontSize=10, leading=13.2,
            textColor=DARK, spaceAfter=1.5,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10.5, leading=15,
            textColor=DARK, spaceAfter=8,
        ),
        "body_small": ParagraphStyle(
            "body_small", fontName="Helvetica", fontSize=10, leading=14,
            textColor=GREY, spaceAfter=4,
        ),
    }


def new_doc(path, title):
    return SimpleDocTemplate(
        path,
        pagesize=PAGE,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=title,
        author="",
        subject=title,
    )


def section_rule():
    return Table(
        [[""]],
        colWidths=[PAGE[0] - MARGIN_LEFT - MARGIN_RIGHT],
        rowHeights=[2],
        style=TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, -1), 0.8, RULE),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        ),
    )


def header_table(left_text, right_text, styles_map):
    left_para = Paragraph(left_text, styles_map["item_header_left"])
    right_para = Paragraph(right_text, styles_map["item_header_right"])
    table = Table(
        [[left_para, right_para]],
        colWidths=[(PAGE[0] - MARGIN_LEFT - MARGIN_RIGHT) * 0.72, (PAGE[0] - MARGIN_LEFT - MARGIN_RIGHT) * 0.28],
        style=TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        ),
    )
    return table


def contact_line(contact):
    parts = []
    for key in ("email", "phone", "location", "linkedin", "github", "portfolio"):
        value = (contact or {}).get(key, "").strip()
        if value:
            parts.append(value.replace("https://", "").replace("http://", ""))
    return "  |  ".join(parts)


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def safe_para(text):
    return escape(text)
