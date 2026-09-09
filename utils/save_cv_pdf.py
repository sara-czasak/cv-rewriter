import os
import re
import markdown
from xhtml2pdf import pisa


def extract_field(text: str, header: str) -> str:
    """Pulls the content under a '## Header' section until the next
    '##' header or end of text."""
    match = re.search(
        rf"##\s*{re.escape(header)}\s*\n(.*?)(?=\n##|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def sanitize_filename(text: str) -> str:
    """Makes a string safe to use in a filename."""
    text = text.strip().replace(" ", "_")
    return re.sub(r'[\\/*?:"<>|]', "", text)


def parse_applicant_name(cv_text: str) -> str:
    """Gets the applicant's name from the CV's Contact section (assumed
    to be the first line under that header)."""
    contact_section = extract_field(cv_text, "Contact")
    first_line = contact_section.splitlines()[0] if contact_section else ""
    if not first_line:
        raise ValueError("Could not find applicant name in CV Contact section.")
    return first_line.strip()


def parse_company(job_posting_text: str) -> str:
    """Gets the company name from the job posting's Company section."""
    company = extract_field(job_posting_text, "Company")
    if not company:
        raise ValueError("Could not find company name in job posting.")
    return company


def save_cv_as_pdf(cv_text: str, job_posting_text: str,
                    output_dir: str = "optimized_cv") -> str:
    """
    Converts the rewritten CV (markdown) to a PDF and saves it as
    {applicant_name}_cv{company}.pdf inside output_dir, creating the
    directory if it doesn't exist.

    Args:
        cv_text (str): The final rewritten CV, in markdown.
        job_posting_text (str): The job posting text (used to pull the
            company name).
        output_dir (str): Directory to save the PDF into. Defaults to
            "optimized_cv".

    Returns:
        str: The full path to the saved PDF.
    """
    applicant_name = sanitize_filename(parse_applicant_name(cv_text))
    company = sanitize_filename(parse_company(job_posting_text))

    os.makedirs(output_dir, exist_ok=True)

    filename = f"{applicant_name}_cv{company}.pdf"
    output_path = os.path.join(output_dir, filename)

    html = markdown.markdown(cv_text)

    with open(output_path, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)

    if pisa_status.err:
        raise RuntimeError(f"Failed to generate PDF for {output_path}")

    return output_path