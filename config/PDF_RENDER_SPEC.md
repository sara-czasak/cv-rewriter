# PDF Render Specification

## Purpose

This specification is for the deterministic PDF renderer, not for the language model.

The renderer must produce a polished, conventional, single-column professional CV.

The AI supplies content. The renderer supplies visual design.

## Page setup

- Paper: A4
- Orientation: portrait
- Layout: single column
- Margins: 18–20 mm on all sides
- Content width: consistent throughout
- No sidebars
- No text boxes
- No tables
- No floating elements

The renderer should allow a CV to flow naturally across pages.

## Typography

Use one professional sans-serif font family throughout.

Recommended:
- Aptos
- Arial
- Calibri
- Liberation Sans
- DejaVu Sans

Use a restrained hierarchy:

- Name: 20–24 pt, bold
- Target title: 11–13 pt
- Section headings: 10–12 pt, bold
- Job titles: 10–11 pt, bold
- Employer: 10–11 pt
- Body: 9.5–10.5 pt
- Dates/location: 9–10 pt

Do not use more than two font families.

## Visual hierarchy

The document should have:
- Strong name at the top
- Clear section headings
- Clearly distinguishable job titles
- Dates visually secondary
- Consistent bullet indentation
- Comfortable line spacing
- Adequate white space

Avoid excessive decoration.

## Color

Use black or near-black body text.

A single restrained accent color may be used for section headings, but the document must remain fully readable when printed in grayscale.

Never use color as the only way to communicate information.

## Header

The first page should begin with:

FULL NAME
Target Professional Title
City | Email | Phone | LinkedIn | Portfolio/GitHub

Only render fields that exist.

Do not use icons as replacements for labels.

## Section spacing

Use consistent spacing:
- Small gap after header
- Moderate gap before each major section
- Small gap after section heading
- Small gap between experience entries
- Tight but readable spacing between bullets

Do not create large empty areas merely for visual effect.

## Experience layout

Recommended visual structure:

JOB TITLE
Employer — Location
Dates

• Achievement/result
• Achievement/result
• Achievement/result

Keep dates aligned consistently, preferably on the same line as employer/location or in a visually secondary line.

Do not use a two-column experience layout.

## Page breaks

Avoid:
- Section headings stranded at the bottom of a page
- A job title separated from its first bullet
- A single bullet stranded on a new page when avoidable
- Excessive blank space

Keep each experience heading with at least one following bullet when possible.

Allow sections to continue naturally onto subsequent pages.

## Length

Target:
- 1 page for early-career candidates when content permits
- 1–2 pages for experienced candidates
- Never remove factual content solely to force one page

If content exceeds two pages, prioritize concise wording and remove redundancy before removing substantive evidence.

## ATS requirements

The final PDF should have:
- Real selectable text
- Normal reading order
- No image-based text
- No tables
- No columns
- No decorative text embedded in images
- Standard headings
- Consistent chronology

The PDF must remain usable when copied and pasted into a plain-text editor.

## Quality gate

Before saving the PDF, automatically verify:

1. Text is selectable.
2. Text extraction preserves reading order.
3. No major section is missing.
4. No text overlaps.
5. No text is clipped.
6. No page contains unexplained large blank regions.
7. Font sizes remain readable.
8. Dates and headings are consistent.
9. The PDF contains the same factual content as the approved structured CV.

If a check fails, regenerate the PDF using the renderer. Do not ask the AI to invent a formatting workaround.
