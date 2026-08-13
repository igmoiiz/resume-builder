# Resume Builder

Generate clean, ATS-friendly, single-column PDF resumes and cover letters from JSON data.

No more reformatting your resume every time you add an achievement — update the data files once and re-run.

## Why this approach

- **ATS-safe by design**: single column, standard Helvetica, no images/graphics/boxes, dates on the same line as the role, and every piece of text is extractable from the PDF.
- **One source of truth**: `data/resume.json` holds *all* your experience, projects, skills, and education once.
- **Title-specific resumes**: profile files (`data/profiles/*.json`) pick which sections to show, in which order, with a tailored summary and skill ordering — no duplicated data.
- **Cover letters**: each job application is a small JSON file rendered into a one-page letter.
- **One dependency**: `reportlab` (pure Python, no LaTeX/WeasyPrint system packages).

## Project layout

```
resume-builder/
├── generate.py               # CLI entry point
├── render/
│   ├── pdf.py                # shared styles, page setup, helpers
│   ├── resume_renderer.py    # builds the resume PDF from data + profile
│   └── cover_renderer.py     # builds cover letter PDFs
├── data/
│   ├── resume.json           # MASTER: contact, skills, experience, education, projects, certs, languages
│   └── profiles/
│       ├── general.json      # sections, summary, selection rules per job title
│       ├── ml-engineer.json
│       └── data-scientist.json
├── cover_letters/
│   └── example.json          # one file per job application
└── output/                   # generated PDFs (git-ignored)
```

## Setup

```bash
cd resume-builder
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
# Generate one resume
.venv/bin/python generate.py --profile general

# Generate multiple profiles at once
.venv/bin/python generate.py --profile ml-engineer --profile data-scientist

# Generate a cover letter
.venv/bin/python generate.py --cover example

# Combine both
.venv/bin/python generate.py --profile ml-engineer --cover example

# List available profiles / cover letters
.venv/bin/python generate.py --list-profiles
.venv/bin/python generate.py --list-covers
```

Output lands in `output/` as `Resume_<Profile>.pdf` and `CoverLetter_<Company>.pdf`.

The script warns you if a resume spills onto a second page.

## Editing your data

### Master file (`data/resume.json`)

Everything lives here. Leave a field as an empty string (`""`) and it is skipped on render.

```json
{
  "name": "Jane Doe",
  "role": "Data Scientist",
  "contact": {
    "email": "jane@example.com",
    "phone": "+1 234 567 8900",
    "location": "City, Country",
    "linkedin": "linkedin.com/in/janedoe",
    "github": "github.com/janedoe",
    "portfolio": ""
  },
  "skills": {
    "programming_languages": ["Python", "SQL"],
    "frameworks_libraries": ["PyTorch", "Pandas"],
    "tools_platforms": ["Docker", "Git"]
  },
  "experience": [
    {
      "id": "my-internship",
      "role": "Data Science Intern",
      "company": "Acme Corp",
      "location": "City, Country",
      "start": "Jun 2025",
      "end": "Sep 2025",
      "bullets": ["Built X that did Y, improving metric by Z%."]
    }
  ],
  "education": [
    {
      "id": "my-degree",
      "degree": "B.S. Computer Science",
      "school": "University",
      "location": "City, Country",
      "start": "Sep 2021",
      "end": "Jun 2025",
      "gpa": "3.8/4.0",
      "highlights": ["Relevant coursework: ..."]
    }
  ],
  "projects": [
    {
      "id": "my-project",
      "name": "Project Name",
      "date": "2025",
      "tech": ["PyTorch", "FastAPI"],
      "summary": "One-line description.",
      "bullets": ["Fine-tuned model to achieve metric."]
    }
  ],
  "certifications": [
    { "id": "c1", "name": "AWS ML Specialty", "issuer": "Amazon", "date": "2025" }
  ],
  "publications": [
    {
      "id": "p1",
      "title": "Title of Your Paper",
      "venue": "Journal Name, Vol. 1(2), pp. 10-20",
      "year": "2026",
      "authors": "Y. Name, Z. Name",
      "link": "https://doi.org/xxxx"
    }
  ],
  "languages": [
    { "id": "l1", "language": "English", "level": "Fluent" }
  ]
}
```

### Profiles (`data/profiles/*.json`)

A profile tailors the same master data to a specific job title:

```json
{
  "filename": "Resume_ML_Engineer",
  "title": "Machine Learning Engineer",
  "summary": "A targeted 2-3 sentence summary for this role.",
  "sections": ["summary", "skills", "experience", "projects", "education", "certifications"],
  "skills": { "order": ["frameworks_libraries", "programming_languages", "tools_platforms"] },
  "experience": { "limit": 4 },
  "projects": { "limit": 4 },
  "certifications": {},
  "languages": {}
}
```

Selection rules:

- `sections`: order and which sections appear. Supported: `summary`, `skills`, `experience`, `projects`, `education`, `certifications`, `publications`, `languages`.
- `skills.order`: display order of skill categories (keys from the master `skills` object).
- `skills.include`: restrict categories (default: all).
- `experience` / `projects` / `education`: `include` (list of item `id`s) and `limit` (max items). Omit `include` to use all entries.
- `certifications` / `languages`: same `include` rule.

To add a new profile (e.g. research assistant), copy an existing profile file, rename it, and adjust the fields.

### Cover letters (`cover_letters/*.json`)

```json
{
  "company": "Acme Data Solutions",
  "role": "Machine Learning Engineer",
  "date": "2026-08-13",
  "recipient": {
    "name": "Hiring Manager",
    "title": "VP of Engineering",
    "company": "Acme Data Solutions",
    "address": ["123 Innovation Drive", "San Francisco, CA 94107"]
  },
  "subject": "Application for Machine Learning Engineer",
  "body": ["Dear Hiring Manager,", "Paragraph one...", "Paragraph two...", "Paragraph three..."],
  "closing": "Sincerely,"
}
```

Leave `date` empty to use today's date. The sender block (name + contact) is pulled from `data/resume.json` automatically.

## Tips for ATS score

- Keep it to **one page**.
- Mirror the exact keywords and phrasing from the job description in your summary and bullets.
- Prefer metric-driven bullets ("improved accuracy by 12%") over generic duties.
- Upload the PDF as-is; do not re-export from a screenshot.

## License

MIT
