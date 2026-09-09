import os
import re
import threading
from flask import Flask, request

app = Flask(__name__)
submitted_event = threading.Event()
submitted_path = None  # <-- set once the form is saved, so main.py can read it back

FIELDS = [
    ("job_title", "Job Title", True),
    ("company_name", "Company", True),
    ("location", "Location", False),
    ("employment_type", "Employment Type", False),
    ("seniority_level", "Seniority Level", False),
    ("short_description", "Short Description", False),
    ("full_description", "Full Description", True),
    ("requirements", "Requirements", True),
    ("nice_to_haves", "Nice-to-Haves", False),
    ("tech_stack", "Tech Stack", False),
    ("compensation", "Compensation", False),
    ("benefits", "Benefits", False),
    ("application_deadline", "Application Deadline", False),
]

@app.route("/", methods=["GET", "POST"])
def form():
    errors = []
    data = {key: "" for key, _, _ in FIELDS}

    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key, _, _ in FIELDS}

        for key, label, required in FIELDS:
            if required and not data[key]:
                errors.append(label)

        if not errors:
            global submitted_path
            submitted_path = save_to_file(data)
            submitted_event.set()
            return "Saved! You can close this tab."

    return render_form(data, errors)

def render_form(data, errors):
    error_html = ""
    if errors:
        missing = ", ".join(errors)
        error_html = (
            f"<p style='color:red;'>Please fill in the following required "
            f"field(s): {missing}</p>"
        )

    inputs = ""
    for key, label, required in FIELDS:
        inputs += f'<label>{label}{" *" if required else ""}</label><br>'
        inputs += (
            f'<textarea name="{key}" rows="4" cols="60">'
            f'{data.get(key, "")}</textarea><br><br>'
        )

    return f"{error_html}<form method='post'>{inputs}<button type='submit'>Save</button></form>"

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def save_to_file(data):
    os.makedirs("jobs", exist_ok=True)

    slug = f"{slugify(data['company_name'])}-{slugify(data['job_title'])}"
    filepath = os.path.join("jobs", f"{slug}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        for key, label, _ in FIELDS:
            f.write(f"## {label}\n{data[key]}\n\n")

    return filepath

if __name__ == "__main__":
    app.run(debug=True, port=5000)