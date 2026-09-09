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
3. **Rewrite the CV** for the posting, then run it through a review loop
   before showing it to you:
   - a **hallucination check** — did the rewrite invent or misrepresent
     anything not in the base CV?
   - a **compatibility re-check** — did the rewrite actually improve (or at
     least not tank) the match score?
   - an **ATS compliance check** — does it hold up against
     `knowledge/ats_guidelines.md` (formatting, keyword presence,
     parseability)?
   - an **Inner Reviewer** pass that weighs all three results and hands down
     PASS or FAIL with a specific issue to fix

     If any check fails, the CV is rewritten and re-checked (capped at 3
     retries per stage) — first as a blind retry, then, once Inner Reviewer
     has flagged a specific issue, as a targeted fix for that issue
     specifically. ✅ built and wired into `main.py`
4. **Output** the final CV as a PDF. 🚧 not yet built — currently the
   approved (or best-effort, if it hit the retry cap) CV is just printed to
   the console.

This is a work in progress. The job-posting form, compatibility check, and
rewrite/review loop are functional end to end; PDF export is still to come.

## Project layout

- `main.py` — entry point. Starts the local Flask form, waits for a job
  posting to be submitted, prompts for the base CV file, runs the
  compatibility check, then runs the rewrite/review loop and prints the
  result.
- `form/app.py` — the local Flask form used to collect job posting details.
  No auth, no external exposure — it's single-user and localhost-only by
  design.
- `template/job_description_template.md` — the markdown template a submitted
  job posting is filled into. Markdown headers were chosen over JSON since
  posting content is mostly free-form prose.
- `jobs/` — where submitted job postings are saved as markdown files (one per
  posting, gitignored — this is your personal data, not project code).
- `steps/` — the pipeline stages that make up the core workflow, each a
  self-contained function `main.py` (or `inner_reviewer.py`) calls in
  sequence:
  - `compatibility_check.py` — scores a CV against a posting
  - `rewrite_cv.py` — rewrites the CV for the posting, optionally targeting a
    specific fix instruction from a prior review pass
  - `hallucination_check.py` — flags anything the rewrite invented or
    misrepresented relative to the base CV
  - `ats_compliance_check.py` — checks a rewrite against the ATS guidelines
  - `inner_reviewer.py` — orchestrates the rewrite/review loop: runs the
    three checks above as a gate, then synthesizes their results into a
    PASS/FAIL verdict with a crucial issue to fix on FAIL
- `prompts/` — the LLM prompt templates, one per step, kept as separate `.md`
  files rather than inlined in Python so they're easy to read and tune
  without touching code.
- `knowledge/ats_guidelines.md` — the ATS formatting/keyword guidelines that
  both the rewrite step and the ATS compliance check are built against.
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
