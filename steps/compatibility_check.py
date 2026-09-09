import re
from py_simple import ask_ai

PROMPT_PATH = "prompts/compatibility_check.md"


def normalize_response(response) -> str:
    """Handles both plain-string and list-of-content-block responses."""
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


def load_prompt(job_posting: str, base_cv: str) -> str:
    """Reads the prompt template and fills in the job posting and CV."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(job_posting=job_posting, base_cv=base_cv)


def parse_scores(response: str) -> dict:
    """
    Pulls HARD_REQUIREMENTS, NICE_TO_HAVES, TRANSFERABLE, and REASONING
    out of the model's response text.
    """
    hard = re.search(r"HARD_REQUIREMENTS:\s*\[?(\d+)\]?", response)
    nice = re.search(r"NICE_TO_HAVES:\s*\[?(\d+)\]?", response)
    transferable = re.search(r"TRANSFERABLE:\s*\[?(\d+)\]?", response)
    reasoning = re.search(r"REASONING:\s*(.+)", response, re.DOTALL)

    if not (hard and nice and transferable and reasoning):
        raise ValueError(f"Could not parse model response:\n{response}")

    return {
        "hard_requirements": int(hard.group(1)),
        "nice_to_haves": int(nice.group(1)),
        "transferable": int(transferable.group(1)),
        "reasoning": reasoning.group(1).strip(),
    }


def calculate_final_score(scores: dict) -> float:
    """Applies the weighted formula: 60% hard reqs, 20% nice-to-haves, 20% transferable."""
    return (
        scores["hard_requirements"] * 0.6
        + scores["nice_to_haves"] * 0.2
        + scores["transferable"] * 0.2
    )


def get_decision(final_score: float) -> str:
    """Maps the final score to a decision band."""
    if final_score < 50:
        return "reject"
    elif final_score <= 80:
        return "ask_user"
    else:
        return "auto_proceed"


def check_compatibility(model, job_posting: str, base_cv: str) -> dict:
    """
    Runs the full compatibility check: builds the prompt, calls the AI,
    parses the response, computes the final score, and returns the
    decision.

    Args:
        model: A model instance from get_model() (e.g. Gemini Flash-Lite).
        job_posting (str): The job posting text.
        base_cv (str): The candidate's base CV text.

    Returns:
        dict with keys: final_score, decision, reasoning, and the raw
        sub-scores (hard_requirements, nice_to_haves, transferable).
    """
    prompt = load_prompt(job_posting, base_cv)
    response = ask_ai(model, prompt)
    response = normalize_response(response)
    scores = parse_scores(response)
    final_score = calculate_final_score(scores)
    decision = get_decision(final_score)

    return {
        "final_score": final_score,
        "decision": decision,
        "reasoning": scores["reasoning"],
        "hard_requirements": scores["hard_requirements"],
        "nice_to_haves": scores["nice_to_haves"],
        "transferable": scores["transferable"],
    }