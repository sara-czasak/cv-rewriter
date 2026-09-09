import re
from py_simple import ask_ai

PROMPT_PATH = "prompts/hallucination_check.md"


def load_prompt(base_cv: str, new_cv: str) -> str:
    """Reads the hallucination-check prompt template and fills in the
    base CV and rewritten CV."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(base_cv=base_cv, new_cv=new_cv)


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
    """Pulls TRUTHFUL and REASONING out of the model's response text."""
    truthful = re.search(r"TRUTHFUL:\s*\[?(TRUE|FALSE)\]?", response, re.IGNORECASE)
    reasoning = re.search(r"REASONING:\s*(.+)", response, re.DOTALL)

    if not (truthful and reasoning):
        raise ValueError(f"Could not parse model response:\n{response}")

    return {
        "truthful": truthful.group(1).upper() == "TRUE",
        "reasoning": reasoning.group(1).strip(),
    }


def check_hallucination(model, base_cv: str, new_cv: str) -> dict:
    """
    Checks whether the rewritten CV is truthful relative to the base CV.

    Args:
        model: A model instance from get_model() (e.g. Gemini Flash-Lite).
        base_cv (str): The candidate's original base CV text.
        new_cv (str): The rewritten CV text to check.

    Returns:
        dict with keys: truthful (bool), reasoning (str).
    """
    prompt = load_prompt(base_cv, new_cv)
    response = ask_ai(model, prompt)
    response = normalize_response(response)
    return parse_result(response)
