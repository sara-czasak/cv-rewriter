import re
from py_simple import ask_ai

PROMPT_PATH = "prompts/ats_compliance_check.md"
ATS_GUIDELINES_PATH = "knowledge/ats_guidelines.md"


def load_prompt(new_cv: str) -> str:
    """Reads the ATS-compliance prompt template and fills in the
    rewritten CV and ATS guidelines."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    with open(ATS_GUIDELINES_PATH, "r", encoding="utf-8") as f:
        ats_guidelines = f.read()
    return template.format(new_cv=new_cv, ats_guidelines=ats_guidelines)


def normalize_response(response) -> str:
    """Handles both plain-string and list-of-content-block responses
    from ask_ai()."""
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


def parse_result(response: str) -> dict:
    """Pulls COMPLIANT and REASONING out of the model's response text."""
    compliant = re.search(r"COMPLIANT:\s*\[?(TRUE|FALSE)\]?", response, re.IGNORECASE)
    reasoning = re.search(r"REASONING:\s*(.+)", response, re.DOTALL)

    if not (compliant and reasoning):
        raise ValueError(f"Could not parse model response:\n{response}")

    return {
        "compliant": compliant.group(1).upper() == "TRUE",
        "reasoning": reasoning.group(1).strip(),
    }


def check_ats_compliance(model, new_cv: str) -> dict:
    """
    Checks whether the rewritten CV complies with ATS guidelines.

    Args:
        model: A model instance from get_model() (e.g. Gemini Flash-Lite).
        new_cv (str): The rewritten CV text to check.

    Returns:
        dict with keys: compliant (bool), reasoning (str).
    """
    prompt = load_prompt(new_cv)
    response = ask_ai(model, prompt)
    response = normalize_response(response)
    return parse_result(response)
