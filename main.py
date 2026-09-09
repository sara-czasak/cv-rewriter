import threading
import webbrowser
import html
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from tkinter import Tk, filedialog
import py_simple as ps
from form.app import app, submitted_event
import os
from dotenv import load_dotenv
import steps.compatibility_check as cc
from utils.extract_text import extract_text
import steps.normalize_cv as normalize_cv
import steps.normalize_job as normalize_job
import steps.inner_reviewer as ir
from utils.save_cv_pdf import save_cv_as_pdf
import form.app as form_app


load_dotenv()

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

def run_server():
    app.run(port=5000, use_reloader=False)


def fetch_job_posting_text(url):
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urlopen(request, timeout=20) as response:
            page_html = response.read().decode("utf-8", errors="ignore")

    except HTTPError as exc:
        raise RuntimeError(
            f"Could not open job posting URL. HTTP status: {exc.code}"
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            f"Could not reach job posting URL: {exc.reason}"
        ) from exc

    page_html = re.sub(
        r"<script.*?>.*?</script>",
        " ",
        page_html,
        flags=re.S | re.I,
    )
    page_html = re.sub(
        r"<style.*?>.*?</style>",
        " ",
        page_html,
        flags=re.S | re.I,
    )
    page_text = re.sub(r"<[^>]+>", "\n", page_html)
    page_text = html.unescape(page_text)
    page_text = re.sub(r"\n\s*\n+", "\n\n", page_text)
    page_text = page_text.strip()

    if not page_text:
        raise RuntimeError("Job posting URL returned no readable text.")

    return page_text


server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

threading.Timer(1, open_browser).start()

submitted_event.wait()

job_posting_path = form_app.submitted_path
job_posting_text = form_app.submitted_job_text
job_posting_url = form_app.submitted_job_url
applicant_name = form_app.submitted_applicant_name

if job_posting_url:
    print(f"Job posting URL received: {job_posting_url}")

elif job_posting_text:
    print("Job posting text received directly.")

else:
    print(f"Job posting saved to: {job_posting_path}")

root = Tk()
root.withdraw()

base_cv = filedialog.askopenfile(
    mode="r",
    filetypes=[
        ("CV Files", "*.txt *.pdf *.docx"),
        ("Text Files", "*.txt"),
        ("PDF Files", "*.pdf"),
        ("Word Documents", "*.docx"),
        ("All Files", "*.*"),
    ]
)
root.destroy()

if base_cv:
    print(f"Base CV loaded from: {base_cv.name}")
else:
    print("No file selected.")


API_KEY = os.getenv("API_KEY")

flash_lite = ps.get_model(
    provider = "google",
    model_name = "gemini-3.5-flash-lite",
    api_key=API_KEY
)

flash = ps.get_model(
    provider = "google",
    model_name="gemini-3.5-flash",
    api_key=API_KEY
)

if job_posting_url:
    job_posting_text = fetch_job_posting_text(job_posting_url)
    job_posting_text = normalize_job.normalize_job(
        flash_lite,
        job_posting_text,
    )

    meaningful_job_text = re.sub(
        r"##\s+[^\n]+\n",
        "",
        job_posting_text,
    ).strip()

    if len(meaningful_job_text) < 200:
        print(
            "\nCould not extract enough job information from this URL."
            "\nSome sites, including LinkedIn, block automated job-page reading."
            "\nPlease restart the app and use 'Paste Job Description' instead.\n"
        )
        raise SystemExit

elif job_posting_text:
    job_posting_text = normalize_job.normalize_job(
        flash_lite,
        job_posting_text,
    )

else:
    with open(job_posting_path, "r", encoding="utf-8") as f:
        job_posting_text = f.read()

raw_base_cv_text = extract_text(base_cv.name)

normalized_cv = normalize_cv.normalize_cv(
    flash_lite,
    raw_base_cv_text,
)
base_cv_text = normalize_cv.cv_to_text(normalized_cv)


result = cc.check_compatibility(flash_lite, job_posting_text, base_cv_text)

print(f"Compatibility score: {result['final_score']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Decision: {result['decision']}")

if result["decision"] == "reject":
    print("\nThis job does not look compatible with the current CV.")
    print(f"Reason: {result['reasoning']}")

    try_another = input(
        "\nWould you like to check against another job? (y/n): "
    ).strip().lower()

    if try_another in ("y", "yes"):
        print("Please restart the app to submit another job posting.")
        raise SystemExit

    print("Stopped.")
    raise SystemExit


if result["decision"] == "ask_user":
    user_choice = input(
        "Compatibility is borderline. Do you want to continue? (y/n): "
    ).strip().lower()

    if user_choice not in ("y", "yes"):
        print("Stopped by user.")
        raise SystemExit

initial_score = result["final_score"]

result = ir.run_review(
    flash,
    flash_lite,
    job_posting_text,
    base_cv_text,
    initial_score,
)

if result["status"] == "approved":
    print("Passed")
    pdf_path = save_cv_as_pdf(result["cv"], job_posting_text, applicant_name)
    print(f"Saved to: {pdf_path}")
else:
    print(f"Needs manual review: {result['reason']}")
    pdf_path = save_cv_as_pdf(
        result["cv"], job_posting_text, applicant_name,
        output_dir="cv_to_review",
    )
    print(f"Saved for manual review to: {pdf_path}")