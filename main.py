import os
import py_simple
import webbrowser
import threading
from form.app import app

with open(
        "./template/job_description_template.md",
        "r",
        encoding='utf-8'
) as f:
    job_description = f.read()

print(job_description)

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")





if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1, open_browser).start()
    app.run(debug=True, port=5000)