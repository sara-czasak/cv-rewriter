import threading
import webbrowser
from tkinter import Tk, filedialog
import py_simple as ps
from form.app import app, submitted_event
import os
from dotenv import load_dotenv
import steps.compatibility_check as cc
from utils.extract_text import extract_text
import steps.rewrite_cv as rw
import steps.inner_reviewer as ir


load_dotenv()

# STEP 1: GET NEEDED DATA
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

def run_server():
    app.run(port=5000, use_reloader=False)


server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

threading.Timer(1, open_browser).start()

submitted_event.wait()

# read the path back off the module now that the event confirms it's set
import form.app as form_app
job_posting_path = form_app.submitted_path
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


# STEP 2: COMPATIBILITY CHECK
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

with open(job_posting_path, "r", encoding="utf-8") as f:
    job_posting_text = f.read()
base_cv_text = extract_text(base_cv.name)


result = cc.check_compatibility(flash_lite, job_posting_text, base_cv_text)

print(f"Compatibility score: {result['final_score']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Decision: {result['decision']}")


rewritten_cv = rw.rewrite_cv(flash, job_posting_text, base_cv_text)
print(rewritten_cv)

result = ir.run_review(flash, flash_lite, job_posting_text, base_cv_text,
                        rewritten_cv, result["final_score"])  # initial_score from your compatibility check

if result["status"] == "approved":
    print("Passed")
else:
    print(f"Needs manual review: {result['reason']}")