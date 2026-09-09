from py_simple import ask_ai

PROMPT_PATH = "prompts/rewrite_cv.md"
ATS_GUIDELINES_PATH = "knowledge/ats_guidelines.md"


def load_prompt(job_posting: str, base_cv: str) -> str:
    """Reads the rewrite prompt template and fills in the job posting,
    base CV, and ATS guidelines."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    with open(ATS_GUIDELINES_PATH, "r", encoding="utf-8") as f:
        ats_guidelines = f.read()
    return template.format(
        job_posting=job_posting,
        base_cv=base_cv,
        ats_guidelines=ats_guidelines,
    )


def normalize_response(response) -> str:
    """Handles both plain-string and list-of-content-block responses
    from ask_ai(). (Same pattern as steps/compatibility_check.py —
    worth moving to a shared utils file once a third step needs it.)"""
    if isinstance(response, str):
        return response
    elif isinstance(response, list):
        parts = []
        for item in response:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n".join(parts)
    else:
        raise TypeError(f"Unexpected response type from ask_ai: {type(response)}")


def rewrite_cv(model, job_posting: str, base_cv: str) -> str:
    """
    Runs the CV rewrite step: builds the prompt (job posting + base CV +
    ATS guidelines), calls the AI, and returns the rewritten CV text.

    Args:
        model: A model instance from get_model() (e.g. Gemini Flash).
        job_posting (str): The job posting text.
        base_cv (str): The candidate's base CV text.

    Returns:
        str: The rewritten CV content, ready for the ATS-compliance
        review step.
    """
    prompt = load_prompt(job_posting, base_cv)
    response = ask_ai(model, prompt)
    return normalize_response(response)
