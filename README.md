# CV Rewriter

A tool that tailors a CV to a specific job posting instead of sending the same
CV to every application. The idea: paste in a job posting, point it at your
base CV, and get back a rewritten, ATS-optimized CV as a PDF — automating the
tailoring step that's easy to skip when doing it by hand for every posting.

## How it works (planned flow)

1. **Collect the job posting** — a local Flask form (localhost only) for
   pasting in the posting's details field by field. ✅ built
2. **Check compatibility** — is this posting actually a realistic match for
   your CV? Scored across hard requirements, nice-to-haves, and transferable
   experience; below 50 rejects, 50–80 asks you to confirm, above 80 proceeds
   automatically. ✅ built and wired into `main.py`
3. **Rewrite the CV** for the posting, then self-check the rewrite against the
   posting's requirements and general ATS compatibility, looping a few times
   until it holds up. 🚧 not yet built
4. **Output** the final CV as a PDF. 🚧 not yet built

This is a work in progress. The job-posting form and the compatibility check
are functional end to end; the rewrite step, ATS check, and PDF export are
still to come.

## Project layout

- `main.py` — entry point. Starts the local Flask form, waits for a job
  posting to be submitted, prompts for the base CV file, then runs the
  compatibility check and prints the result.
- `form/app.py` — the local Flask form used to collect job posting details.
  No auth, no external exposure — it's single-user and localhost-only by
  design.
- `template/job_description_template.md` — the markdown template a submitted
  job posting is filled into. Markdown headers were chosen over JSON since
  posting content is mostly free-form prose.
- `jobs/` — where submitted job postings are saved as markdown files (one per
  posting, gitignored — this is your personal data, not project code).
- `steps/` — the pipeline stages that make up the core workflow (currently
  `compatibility_check.py`). Each step is meant to be a self-contained
  function `main.py` calls in sequence — this is where the rewrite and ATS
  check steps will live once built.
- `prompts/` — the LLM prompt templates, one per step, kept as separate `.md`
  files rather than inlined in Python so they're easy to read and tune
  without touching code.
- `utils/extract_text.py` — pulls plain text out of `.txt`, `.pdf`, or
  `.docx` files by extension. Shared by any step that needs to read the base
  CV off disk.

## Running it

```
python main.py
```

This starts the form server, opens it in your browser, and once you submit a
job posting, prompts you to pick your base CV file (`.txt`, `.pdf`, or
`.docx`).

## Requirements

- Python 3
- Flask
- `py_simple` (handles the LLM call — currently configured for Gemini)
- `pypdf` and `python-docx` (reading `.pdf` / `.docx` base CVs)
- `python-dotenv`
- A `.env` file with `API_KEY` set to your Gemini API key
