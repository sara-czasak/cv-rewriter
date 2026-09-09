from flask import Flask, request

app = Flask(__name__)

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
    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key, _, _ in FIELDS}
        save_to_file(data)
        return "Saved! You can close this tab."

    # build the form HTML
    inputs = ""
    for key, label, required in FIELDS:
        inputs += f'<label>{label}{" *" if required else ""}</label><br>'
        inputs += f'<textarea name="{key}" rows="4" cols="60"></textarea><br><br>'

    return f"<form method='post'>{inputs}<button type='submit'>Save</button></form>"

def save_to_file(data):
    with open("job_posting.md", "w", encoding="utf-8") as f:
        for key, label, _ in FIELDS:
            f.write(f"## {label}\n{data[key]}\n\n")

if __name__ == "__main__":
    app.run(debug=True, port=5000)