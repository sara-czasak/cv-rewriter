# CV Template Specification

## Purpose
Generate CV content that is professional, ATS-friendly, readable by humans, and suitable for deterministic PDF rendering.

The AI must control **content only**. Do not attempt to control PDF coordinates, fonts, margins, columns, or page breaks. Those are controlled by the PDF renderer.

## Required document structure

Use this section order unless a section is genuinely absent:

1. Header
2. Professional Summary
3. Core Skills
4. Professional Experience
5. Education
6. Certifications
7. Additional Information

### Header
Include:
- Full name
- Professional title / target role
- City and country, if present in the base CV
- Email, phone, LinkedIn, portfolio/GitHub, if present

Never invent contact information.

### Professional Summary
- 3–5 sentences.
- Tailor it to the target job.
- Prioritize experience and strengths supported by the base CV.
- Do not introduce new employers, titles, technologies, achievements, metrics, or years.
- Avoid generic filler such as "results-driven professional" unless it conveys a specific supported strength.

### Core Skills
- Use a simple list of skills, not a table.
- Prefer 10–18 highly relevant skills.
- Put the most job-relevant supported skills first.
- Do not add a skill merely because it appears in the job description.
- A skill may be included only when supported by the base CV or an explicitly approved source.

### Professional Experience
For each role:
- Job title
- Employer
- Location, if available
- Dates
- 3–6 achievement-oriented bullets where source material supports them

Bullet rules:
- Start with a strong action verb where appropriate.
- Be concise.
- Prefer impact and outcomes over task lists.
- Preserve factual meaning.
- Never fabricate numbers, percentages, team sizes, budgets, technologies, clients, awards, promotions, or outcomes.
- Do not change employment dates or job titles unless explicitly instructed.

### Education
Include degree/qualification, institution, and dates when available.

### Certifications
Include only certifications supported by the source CV.

### Additional Information
Use only when supported and useful for the target role.

## ATS formatting rules

The generated content must be compatible with a single-column PDF template.

DO NOT use:
- Tables
- Multi-column layouts
- Text boxes
- Sidebars
- Icons used instead of text
- Decorative graphics
- Logos
- Skill bars
- Star/rating systems
- Progress bars
- Headers/footers containing essential CV information
- Important information conveyed only through color
- Unusual Unicode symbols as structural separators

Use:
- Plain text section headings
- Conventional job titles
- Standard date formats
- Standard section names
- Short bullet points
- Consistent terminology
- Normal punctuation

## Keyword tailoring

When tailoring for a job:
1. Identify relevant keywords in the job description.
2. Match them to evidence in the base CV.
3. Naturally incorporate supported terminology.
4. Never keyword-stuff.
5. Never claim experience that is not supported.

Use the employer's terminology when it accurately describes existing experience.

## Output contract

The model should return structured data matching the application's CV schema.

If a plain-text representation is required, use:

# FULL NAME
TARGET TITLE
Contact line

## PROFESSIONAL SUMMARY
...

## CORE SKILLS
Skill 1 | Skill 2 | Skill 3

## PROFESSIONAL EXPERIENCE
### JOB TITLE — EMPLOYER
Location | Dates
- Achievement
- Achievement

## EDUCATION
...

## CERTIFICATIONS
...

## ADDITIONAL INFORMATION
...

Do not add commentary before or after the CV.
