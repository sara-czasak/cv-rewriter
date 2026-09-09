import os
import re
import tempfile
import threading
from flask import Flask, request
from utils.extract_text import extract_text

app = Flask(__name__)
submitted_event = threading.Event()
submitted_path = None
submitted_job_text = None
submitted_job_url = None
submitted_applicant_name = None
submitted_company_name = None

INPUT_MODES = [
    ("paste", "Paste Job Description"),
    ("url", "Job Posting URL"),
    ("upload", "Upload Job Description"),
    ("form", "Full Job Details Form"),
]

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

# Not written into the job posting markdown — used only for the output CV filename
APPLICANT_FIELD = ("applicant_name", "Your Name (for CV filename)", True)

@app.route("/", methods=["GET", "POST"])
def form():
    errors = []
    data = {key: "" for key, _, _ in FIELDS}
    data[APPLICANT_FIELD[0]] = ""
    data["input_mode"] = "paste"

    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key, _, _ in
                FIELDS}
        data["input_mode"] = request.form.get("input_mode",
                                              "paste").strip()
        data["job_text"] = request.form.get("job_text", "").strip()
        data["job_url"] = request.form.get("job_url", "").strip()
        job_file = request.files.get("job_file")

        applicant_key, applicant_label, applicant_required = APPLICANT_FIELD
        data[applicant_key] = request.form.get(applicant_key, "").strip()

        if data["input_mode"] == "form":
            for key, label, required in FIELDS:
                if required and not data[key]:
                    errors.append(label)


        elif data["input_mode"] == "paste":

            if not data["job_text"]:
                errors.append("Paste Job Description")



        elif data["input_mode"] == "url":

            if not data["job_url"]:
                errors.append("Job Posting URL")


        elif data["input_mode"] == "upload":

            if not job_file or not job_file.filename:
                errors.append("Upload Job Description")

        if applicant_required and not data[applicant_key]:
            errors.append(applicant_label)

        if not errors:
            global submitted_path, submitted_job_text, submitted_job_url, submitted_applicant_name

            submitted_applicant_name = data[applicant_key]

            if data["input_mode"] == "paste":
                submitted_job_text = data["job_text"]
                submitted_path = None
                submitted_job_url = None


            elif data["input_mode"] == "url":
                submitted_job_url = data["job_url"]
                submitted_job_text = None
                submitted_path = None

            elif data["input_mode"] == "upload":
                suffix = os.path.splitext(job_file.filename)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False,
                                                 suffix=suffix) as temp_file:
                    temp_path = temp_file.name
                try:
                    job_file.save(temp_path)
                    submitted_job_text = extract_text(temp_path)
                    submitted_path = None
                    submitted_job_url = None
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            elif data["input_mode"] == "form":
                submitted_path = save_to_file(data)
                submitted_job_text = None
                submitted_job_url = None
            submitted_event.set()
            return "Submitted! You can close this tab."
    return render_form(data, errors)


def render_form(data, errors):
    error_html = ""
    if errors:
        missing = ", ".join(errors)
        error_html = (
            f"<p style='color:red;'>Please fill in the following required "
            f"field(s): {missing}</p>"
        )

    applicant_key, applicant_label, applicant_required = APPLICANT_FIELD
    inputs = f'<label>{applicant_label}{" *" if applicant_required else ""}</label><br>'
    inputs += (
        f'<input type="text" name="{applicant_key}" '
        f'value="{data.get(applicant_key, "")}"><br><br>'
    )
    inputs += '<label>Job Description Input *</label><br>'
    inputs += '<select name="input_mode" id="input_mode">'
    for mode_value, mode_label in INPUT_MODES:
        selected = " selected" if data.get("input_mode",
                                           "paste") == mode_value else ""
        inputs += (
            f'<option value="{mode_value}"{selected}>'
            f'{mode_label}'
            f'</option>'
        )
    inputs += '</select><br><br>'
    inputs += f"""
    <div id="paste_mode">
        <label>Paste Job Description *</label><br>
        <textarea name="job_text" rows="16" cols="80">{data.get("job_text", "")}</textarea><br><br>
    </div>

    <div id="url_mode" style="display:none;">
        <label>Job Posting URL *</label><br>
        <input type="url" name="job_url" size="80"><br><br>
    </div>

    <div id="upload_mode" style="display:none;">
        <label>Upload Job Description *</label><br>
        <input type="file" name="job_file" accept=".txt,.md,.pdf,.docx"><br><br>
    </div>

    <div id="form_mode" style="display:none;">
    """

    for key, label, required in FIELDS:
        inputs += f'<label>{label}{" *" if required else ""}</label><br>'
        inputs += (
            f'<textarea name="{key}" rows="4" cols="60">'
            f'{data.get(key, "")}</textarea><br><br>'
        )
    inputs += """
    </div>

    <script>
        const inputMode = document.getElementById("input_mode");

        function updateInputMode() {
            const mode = inputMode.value;

            document.getElementById("paste_mode").style.display =
                mode === "paste" ? "block" : "none";

            document.getElementById("url_mode").style.display =
                mode === "url" ? "block" : "none";

            document.getElementById("upload_mode").style.display =
                mode === "upload" ? "block" : "none";

            document.getElementById("form_mode").style.display =
                mode === "form" ? "block" : "none";
        }

        inputMode.addEventListener("change", updateInputMode);
        updateInputMode();
    </script>
    """

    return (
        f"{error_html}"
        f"<form method='post' enctype='multipart/form-data'>"
        f"{inputs}"
        f"<button type='submit'>Save</button>"
        f"</form>"
    )

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