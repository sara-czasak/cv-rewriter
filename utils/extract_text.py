from pypdf import PdfReader
from docx import Document

def extract_text(file_path: str) -> str:
    """Reads text from a .txt, .pdf, or .docx file, based on extension."""
    extension = file_path.lower().rsplit(".", 1)[-1]

    if extension == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif extension == "pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif extension == "docx":
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: .{extension}")