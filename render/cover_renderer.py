import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch

from render import pdf as pdfkit


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _format_date(value):
    if not value:
        today = date.today()
        return f"{today.day} {MONTHS[today.month - 1]} {today.year}"
    try:
        year, month, day = value.split("-")
        return f"{int(day)} {MONTHS[int(month) - 1]} {int(year)}"
    except (ValueError, AttributeError):
        return str(value)


def _clean(value):
    return (value or "").strip()


def render_cover_letter(data, letter, output_path):
    styles = pdfkit.styles()
    story = []

    name = data.get("name", "")
    if name:
        story.append(Paragraph(pdfkit.escape(name), styles["name"]))

    contact = pdfkit.contact_line(data.get("contact", {}))
    if contact:
        story.append(Paragraph(pdfkit.escape(contact), styles["contact"]))

    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph(pdfkit.escape(_format_date(letter.get("date"))), styles["body_small"]))
    story.append(Spacer(1, 0.12 * inch))

    recipient = letter.get("recipient", {}) or {}
    for key in ("name", "title", "company"):
        value = _clean(recipient.get(key))
        if value:
            story.append(Paragraph(pdfkit.escape(value), styles["body_small"]))
    for line in recipient.get("address", []) or []:
        line = _clean(line)
        if line:
            story.append(Paragraph(pdfkit.escape(line), styles["body_small"]))

    story.append(Spacer(1, 0.3 * inch))

    subject = _clean(letter.get("subject"))
    if not subject:
        subject = f"Application for {letter.get('role', '')} at {letter.get('company', '')}"
    if subject:
        story.append(Paragraph(f"<b>Re: {pdfkit.escape(subject)}</b>", styles["body"]))
        story.append(Spacer(1, 0.05 * inch))

    for para in letter.get("body", []) or []:
        para = _clean(para)
        if para:
            story.append(Paragraph(pdfkit.escape(para), styles["body"]))

    closing = _clean(letter.get("closing")) or "Sincerely,"
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(pdfkit.escape(closing), styles["body"]))
    story.append(Spacer(1, 0.35 * inch))
    if name:
        story.append(Paragraph(f"<b>{pdfkit.escape(name)}</b>", styles["body"]))

    doc = pdfkit.new_doc(output_path, f"{name} - Cover Letter")
    doc.build(story)
    return output_path
