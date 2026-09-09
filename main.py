import threading
import webbrowser
from tkinter import Tk, filedialog
import py_simple as ps
from form.app import app, submitted_event

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

def run_server():
    app.run(port=5000, use_reloader=False)

if __name__ == "__main__":
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