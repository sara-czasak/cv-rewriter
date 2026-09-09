from py_simple import ask_ai


PROMPT_PATH = "prompts/normalize_job.md"


def _response_to_text(response):
    if isinstance(response, str):
        return response.strip()

    if isinstance(response, list):
        return "\n".join(
            str(item)
            for item in response
            if item is not None
        ).strip()

    return str(response).strip()


def normalize_job(model, job_posting_text: str) -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.replace("{job_posting}", job_posting_text)

    response = ask_ai(model, prompt)
    normalized_job = _response_to_text(response)

    if not normalized_job:
        raise ValueError("Job posting normalization returned no text.")

    company_marker = "## Company"

    if company_marker not in normalized_job:
        raise ValueError(
            "Could not identify company name from job posting.")

    company_section = (
        normalized_job
        .split(company_marker, 1)[1]
        .split("\n##", 1)[0]
        .strip()
    )

    if not company_section:
        raise ValueError(
            "Could not identify company name from job posting.")

    return normalized_job