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


def parse_company(job_posting_text: str) -> str:
    """Gets the company name from the job posting's Company section."""
    company = extract_field(job_posting_text, "Company")
    if not company:
        raise ValueError("Could not find company name in job posting.")
    return company


def save_cv_as_pdf(cv_text: str, job_posting_text: str, applicant_name: str,
                    output_dir: str = "optimized_cv") -> str:
    """
    Converts the rewritten CV (markdown) to a PDF and saves it as
    {applicant_name}_cv{company}.pdf inside output_dir, creating the
    directory if it doesn't exist.

    Args:
        cv_text (str): The final rewritten CV, in markdown.
        job_posting_text (str): The job posting text (used to pull the
            company name).
        applicant_name (str): The applicant's name, as entered in the
            job-posting form. Used only for the output filename.
        output_dir (str): Directory to save the PDF into. Defaults to
            "optimized_cv".

    Returns:
        str: The full path to the saved PDF.
    """
    applicant_name = sanitize_filename(applicant_name)
    company = sanitize_filename(parse_company(job_posting_text))

    os.makedirs(output_dir, exist_ok=True)

    filename = f"{applicant_name}_cv{company}.pdf"
    output_path = os.path.join(output_dir, filename)

    body_html = markdown.markdown(cv_text)

    html = f"""
    <html>
    <head>
    <style>
        @page {{
            size: A4;
            margin: 16mm 18mm;
        }}

        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 9.5pt;
            line-height: 1.3;
            color: #000000;
        }}

        h1 {{
            font-size: 18pt;
            margin: 0 0 4px 0;
            padding: 0;
            font-weight: bold;
        }}

        h2 {{
            font-size: 11pt;
            margin: 12px 0 5px 0;
            padding: 0 0 2px 0;
            font-weight: bold;
            border-bottom: 0.5px solid #000000;
        }}

        h3 {{
            font-size: 10pt;
            margin: 7px 0 1px 0;
            padding: 0;
            font-weight: bold;
        }}

        p {{
            margin: 1px 0 3px 0;
            padding: 0;
        }}

        ul {{
            margin: 2px 0 5px 14px;
            padding: 0;
        }}

        li {{
            margin: 0 0 2px 0;
            padding: 0;
        }}
    </style>
    </head>
    <body>
    {body_html}
    </body>
    </html>
    """

    with open(output_path, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)

    if pisa_status.err:
        raise RuntimeError(f"Failed to generate PDF for {output_path}")

    return output_path