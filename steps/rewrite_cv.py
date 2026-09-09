from py_simple import ask_ai

PROMPT_PATH = "prompts/rewrite_cv.md"
ATS_GUIDELINES_PATH = "knowledge/ats_guidelines.md"


def load_prompt(job_posting: str, base_cv: str, fix_instruction: str = None) -> str:
    """Reads the rewrite prompt template and fills in the job posting,
    base CV, ATS guidelines, and (optionally) a specific issue to fix
    from a previous Inner Reviewer verdict."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    with open(ATS_GUIDELINES_PATH, "r", encoding="utf-8") as f:
        ats_guidelines = f.read()

    if fix_instruction:
        fix_instruction_section = (
            f"\nIMPORTANT — the previous rewrite attempt was rejected for "
            f"this specific reason. Address it directly in this rewrite:\n"
            f"{fix_instruction}\n"
        )
    else:
        fix_instruction_section = ""

    return template.format(
        job_posting=job_posting,
        base_cv=base_cv,
        ats_guidelines=ats_guidelines,
        fix_instruction_section=fix_instruction_section,
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


def rewrite_cv(model, job_posting: str, base_cv: str, fix_instruction: str = None) -> str:
    """
    Runs the CV rewrite step: builds the prompt (job posting + base CV +
    ATS guidelines + optional fix instruction), calls the AI, and
    returns the rewritten CV text.

    Args:
        model: A model instance from get_model() (e.g. Gemini Flash).
        job_posting (str): The job posting text.
        base_cv (str): The candidate's base CV text.
        fix_instruction (str, optional): A specific issue flagged by
            Inner Reviewer on a previous attempt, to address directly
            in this rewrite. Defaults to None (a blind/fresh rewrite).

    Returns:
        str: The rewritten CV content, ready for the ATS-compliance
        review step.
    """
    prompt = load_prompt(job_posting, base_cv, fix_instruction)
    response = ask_ai(model, prompt)
    return normalize_response(response)