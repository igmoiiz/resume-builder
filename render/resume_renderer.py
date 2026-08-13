import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.platypus import KeepTogether, Paragraph, Spacer

from render import pdf as pdfkit

WORD_MAP = {"ml": "ML", "mlops": "MLOps", "ai": "AI", "cv": "CV", "api": "API"}


def _clean(value):
    return (value or "").strip()


def _label(category):
    words = category.replace("_", " ").title().split()
    return " ".join(WORD_MAP.get(word.lower(), word) for word in words)


class ResumeRenderer:
    def __init__(self, data, profile):
        self.data = data
        self.profile = profile
        self.styles = pdfkit.styles()

    def build(self):
        story = []
        story += self._header()
        for section in self.profile.get("sections", []):
            flowables = getattr(self, f"_section_{section}", lambda: [])()
            if flowables:
                story.append(Paragraph(section.replace("_", " ").upper(), self.styles["section"]))
                story.append(pdfkit.section_rule())
                story += flowables
        return story

    def _header(self):
        name = self.data.get("name", "")
        role = self.profile.get("title") or self.data.get("role", "")
        contact = pdfkit.contact_line(self.data.get("contact", {}))
        flowables = []
        if name:
            flowables.append(Paragraph(pdfkit.escape(name), self.styles["name"]))
        if role:
            flowables.append(Paragraph(pdfkit.escape(role), self.styles["role"]))
        if contact:
            flowables.append(Paragraph(pdfkit.escape(contact), self.styles["contact"]))
        return flowables

    def _section_summary(self):
        summary = self.profile.get("summary") or self.data.get("summary", "")
        summary = _clean(summary)
        if not summary:
            return []
        return [Paragraph(pdfkit.escape(summary), self.styles["body"])]

    def _section_skills(self):
        skills = self.data.get("skills", {})
        cfg = self.profile.get("skills", {}) or {}
        order = cfg.get("order") or list(skills.keys())
        include = set(cfg.get("include") or skills.keys())
        flowables = []
        for category in order:
            items = [i for i in skills.get(category, []) if _clean(i)]
            if category not in include or not items:
                continue
            text = f"<b>{pdfkit.escape(_label(category))}:</b> {pdfkit.escape(', '.join(items))}"
            flowables.append(Paragraph(text, self.styles["skills_line"]))
        return flowables

    def _section_experience(self):
        return self._render_experience(self.data.get("experience", []), self.profile.get("experience", {}))

    def _render_experience(self, entries, cfg):
        selected = self._select(entries, cfg)
        flowables = []
        for entry in selected:
            role = _clean(entry.get("role"))
            company = _clean(entry.get("company"))
            location = _clean(entry.get("location"))
            start = _clean(entry.get("start"))
            end = _clean(entry.get("end"))
            left = pdfkit.escape(role)
            if company:
                left += f" at {pdfkit.escape(company)}"
            if location:
                left += f", {pdfkit.escape(location)}"
            right = " to ".join([d for d in (start, end) if d])
            group = [pdfkit.header_table(f"<b>{left}</b>", pdfkit.escape(right), self.styles)]
            group += self._bullets(entry.get("bullets", []))
            flowables.append(KeepTogether(group))
        return flowables

    def _section_projects(self):
        entries = self.data.get("projects", [])
        cfg = self.profile.get("projects", {}) or {}
        selected = self._select(entries, cfg)
        flowables = []
        for entry in selected:
            name = _clean(entry.get("name"))
            date = _clean(entry.get("date"))
            tech = [t for t in entry.get("tech", []) if _clean(t)]
            summary = _clean(entry.get("summary"))
            left = f"<b>{pdfkit.escape(name)}</b>"
            group = [pdfkit.header_table(left, pdfkit.escape(date), self.styles)]
            if tech:
                group.append(Paragraph(f"Tech: {pdfkit.escape(', '.join(tech))}", self.styles["project_tech"]))
            if summary and not entry.get("bullets"):
                group.append(Paragraph(pdfkit.escape(summary), self.styles["detail_line"]))
            group += self._bullets(entry.get("bullets", []))
            flowables.append(KeepTogether(group))
        return flowables

    def _section_education(self):
        entries = self.data.get("education", [])
        cfg = self.profile.get("education", {}) or {}
        selected = self._select(entries, cfg)
        flowables = []
        for entry in selected:
            degree = _clean(entry.get("degree"))
            school = _clean(entry.get("school"))
            location = _clean(entry.get("location"))
            start = _clean(entry.get("start"))
            end = _clean(entry.get("end"))
            gpa = _clean(entry.get("gpa"))
            left = pdfkit.escape(degree)
            if school:
                left += f", {pdfkit.escape(school)}"
            right = " to ".join([d for d in (start, end) if d])
            group = [pdfkit.header_table(f"<b>{left}</b>", pdfkit.escape(right), self.styles)]
            detail = []
            if location:
                detail.append(pdfkit.escape(location))
            if gpa:
                detail.append(pdfkit.escape(gpa))
            if detail:
                group.append(Paragraph(" · ".join(detail), self.styles["detail_line"]))
            group += self._bullets(entry.get("highlights", []))
            flowables.append(KeepTogether(group))
        return flowables

    def _section_certifications(self):
        entries = self.data.get("certifications", [])
        cfg = self.profile.get("certifications", {}) or {}
        selected = self._select(entries, cfg)
        flowables = []
        for entry in selected:
            name = _clean(entry.get("name"))
            issuer = _clean(entry.get("issuer"))
            date = _clean(entry.get("date"))
            text = name
            if issuer:
                text += f", {issuer}"
            if date:
                text += f" ({date})"
            flowables.append(Paragraph(pdfkit.escape(text), self.styles["skills_line"]))
        return flowables

    def _section_publications(self):
        entries = self.data.get("publications", [])
        cfg = self.profile.get("publications", {}) or {}
        selected = self._select(entries, cfg)
        flowables = []
        for entry in selected:
            title = _clean(entry.get("title"))
            venue = _clean(entry.get("venue"))
            year = _clean(entry.get("year"))
            authors = _clean(entry.get("authors"))
            link = _clean(entry.get("link"))
            if not title:
                continue
            text = f"<b>{pdfkit.escape(title)}</b>"
            if venue:
                text += f". {pdfkit.escape(venue)}"
            if year:
                text += f" ({year})"
            if authors:
                text += f"<br/><font color='#555555'>{pdfkit.escape(authors)}</font>"
            if link:
                text += f"<br/><font color='#555555'>{pdfkit.escape(link)}</font>"
            flowables.append(Paragraph(text, self.styles["skills_line"]))
        return flowables

    def _section_languages(self):
        entries = self.data.get("languages", [])
        cfg = self.profile.get("languages", {}) or {}
        selected = self._select(entries, cfg)
        parts = []
        for entry in selected:
            language = _clean(entry.get("language"))
            level = _clean(entry.get("level"))
            if language:
                parts.append(f"{language} ({level})" if level else language)
        if not parts:
            return []
        return [Paragraph(pdfkit.escape(" · ".join(parts)), self.styles["skills_line"])]

    def _bullets(self, bullets):
        flowables = []
        for bullet in bullets:
            bullet = _clean(bullet)
            if not bullet:
                continue
            flowables.append(Paragraph(pdfkit.escape(bullet), self.styles["bullet"], bulletText="\u2022"))
        return flowables

    def _select(self, entries, cfg):
        include = cfg.get("include") or []
        limit = cfg.get("limit")
        if include:
            id_map = {entry.get("id"): entry for entry in entries}
            selected = [id_map[i] for i in include if i in id_map]
        else:
            selected = list(entries)
        if limit and limit > 0:
            selected = selected[:limit]
        return selected


def render_resume(data, profile, output_path):
    renderer = ResumeRenderer(data, profile)
    story = renderer.build()

    page_count = {"n": 0}

    def page_callback(canvas, doc):
        page_count["n"] = canvas.getPageNumber()

    doc = pdfkit.new_doc(output_path, f"{data.get('name', '')} - Resume")
    doc.build(story, onFirstPage=page_callback, onLaterPages=page_callback)

    if page_count["n"] > 1:
        print(f"[warn] Resume is {page_count['n']} pages, consider trimming bullets or sections.")
    return output_path
