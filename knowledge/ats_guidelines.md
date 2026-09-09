# ATS Guidelines

Reference knowledge for how Applicant Tracking Systems actually process CVs.
Injected into the Rewrite CV and ATS-compliance-check prompts so the model
optimizes against real mechanics, not guesswork.

## How ATS Systems Work

1. **Parser** extracts structured fields from the file: contact info, work
   history (company, title, dates), education, skills.
2. **Matcher** compares those extracted fields against the job description
   and recruiter filters, using keyword matching and (on modern systems)
   semantic scoring.
3. **If parsing fails, ranking defaults to zero** — regardless of how
   qualified the candidate actually is. Parsing failure is the single
   biggest cause of good candidates getting filtered out, more than weak
   keyword matching.

## Formatting Rules (parser-safe)

- Single-column layout only — no tables, sidebars, text boxes, icons, or
  graphics
- Standard section headings: Contact, Summary, Skills, Experience,
  Education, Certifications
- Reverse-chronological order (most recent role first)
- No text embedded inside images or logos
- 1-2 pages for early/mid-career; avoid page 3+ outside specialized fields

## Keyword Rules

- Mirror the job posting's actual terminology — use the same words the
  posting uses, not just synonyms
- Place the most important matching keywords prominently: in the summary
  and in the first bullet under each relevant role
- Do not keyword-stuff or use hidden/white text tricks — modern ATS
  platforms (Workday, Greenhouse, Lever, etc.) actively detect this and
  flag it as fraud, which can auto-reject the application
- Bullets should be outcome-led with concrete metrics, scope, and tools —
  not bare duty descriptions

## File Format

- Plain `.docx` parses most reliably across ATS platforms
- A genuinely text-based PDF (exported from Word/Google Docs, not a
  scanned image or a designer PDF from Canva/Figma) is also acceptable
- Avoid visually designed PDFs with complex layouts — they are the
  leading cause of parsing failures
