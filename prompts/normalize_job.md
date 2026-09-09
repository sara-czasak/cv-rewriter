You are normalizing a raw job posting into a consistent Markdown structure.

Do not invent information.
Do not add requirements, technologies, benefits, compensation, or other facts that are not present in the source.
Preserve the meaning of the original posting.
Extract information where it is clearly available.

Return only Markdown.
Do not use code fences.
Do not include commentary before or after the Markdown.

Use exactly these headings, in this order:

## Job Title
Job title, if identifiable.

## Company
Company name, if identifiable.

## Location
Location or remote/hybrid information, if identifiable.

## Employment Type
Employment type, if identifiable.

## Seniority Level
Seniority level, if identifiable.

## Short Description
A concise description based only on the source posting.

## Full Description
The main job description and responsibilities.

## Requirements
Required qualifications, skills, experience, technologies, or responsibilities.

## Nice-to-Haves
Preferred or optional qualifications.

## Tech Stack
Technologies, programming languages, frameworks, platforms, tools, and databases explicitly mentioned.

## Compensation
Compensation information, if present.

## Benefits
Benefits, if present.

## Application Deadline
Application deadline, if present.

If a field cannot be identified, leave its section empty.

Raw job posting:

{job_posting}