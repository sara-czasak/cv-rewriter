You are rewriting a candidate's CV to tailor it to a specific job posting, optimized for both ATS parsing and human readability.

JOB POSTING: {job_posting}

CANDIDATE'S BASE CV: {base_cv}

ATS GUIDELINES (follow these strictly): {ats_guidelines} {fix_instruction_section} Instructions:

Rewrite the CV so it clearly reflects the candidate's fit for this specific posting — reorder, re-emphasize, and rephrase existing content to match the posting's language and priorities.
Do NOT invent experience, skills, job titles, dates, or qualifications the candidate does not have. Every claim in the rewritten CV must be traceable to something present in the base CV.
Follow the ATS guidelines above for formatting, section order, keyword placement, and file-format-safe structure.
Use outcome-led bullets with concrete metrics, scope, or tools where the base CV provides enough detail to support them. Do not fabricate numbers that aren't in the base CV.
Mirror the job posting's own terminology where the candidate's actual experience genuinely matches it.

Output ONLY the rewritten CV content as clean Markdown, with no commentary, explanation, or notes outside the CV.

Use this exact structural format:

# Candidate Name

Candidate Title

Contact details must each appear on their own separate line. Do not use pipes, tables, columns, or inline separators.

## Summary

Summary text.

## Skills

- Skill category: skill, skill, skill
- Skill category: skill, skill, skill

## Experience

### Job Title

Employer

Location, if present

Dates

- Achievement or responsibility
- Achievement or responsibility
- Achievement or responsibility

Repeat that exact structure for every experience entry.

## Education

### Degree or Qualification

Institution

Location, if present

Dates, if present

## Certifications

- Certification
- Certification

Formatting requirements:
- The candidate's name must be the only text in the H1 heading.
- Never place the candidate's name, contact information, or title on the same line.
- Use H2 headings for CV sections.
- Use H3 headings for job titles and education qualifications.
- Employer, location, and dates must each be on separate lines.
- Experience responsibilities and achievements must always be Markdown bullet points beginning with "- ".
- Skills must be Markdown bullet points.
- Certifications must be Markdown bullet points.
- Never combine a job title, employer, dates, and first bullet into one paragraph.
- Never use pipes ("|"), tables, columns, HTML, or code fences.
- Preserve all factual information from the base CV unless tailoring legitimately requires reordering or rephrasing it.
- Omit any section for which the base CV contains no content.