import re
from py_simple import ask_ai
import steps.hallucination_check as hallucination_check
import steps.compatibility_check as compatibility_check
import steps.ats_compliance_check as ats_compliance_check
import steps.rewrite_cv as rewrite_cv

PROMPT_PATH = "prompts/inner_reviewer.md"
COMPATIBILITY_DROP_THRESHOLD = 25
MAX_RETRIES = 3


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


def load_prompt(hallucination_result: dict, initial_score: float,
                 new_score: float, ats_result: dict) -> str:
    """Fills in the Inner Reviewer prompt with the gathered check results."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(
        hallucination_truthful=hallucination_result["truthful"],
        hallucination_reasoning=hallucination_result["reasoning"],
        initial_score=initial_score,
        new_score=new_score,
        ats_compliant=ats_result["compliant"],
        ats_reasoning=ats_result["reasoning"],
    )


def parse_verdict(response: str) -> dict:
    """Pulls VERDICT and CRUCIAL_ISSUE out of the model's response text."""
    verdict = re.search(r"VERDICT:\s*\[?(PASS|FAIL)\]?", response, re.IGNORECASE)
    issue = re.search(r"CRUCIAL_ISSUE:\s*(.+)", response, re.DOTALL)

    if not (verdict and issue):
        raise ValueError(f"Could not parse model response:\n{response}")

    return {
        "verdict": verdict.group(1).upper(),
        "crucial_issue": issue.group(1).strip(),
    }


def run_inner_reviewer(model, hallucination_result: dict, initial_score: float,
                        new_score: float, ats_result: dict) -> dict:
    """Calls the Inner Reviewer synthesis step with all gathered data."""
    prompt = load_prompt(hallucination_result, initial_score, new_score, ats_result)
    response = ask_ai(model, prompt)
    response = normalize_response(response)
    return parse_verdict(response)


def run_review(model_flash, model_flash_lite, job_posting: str, base_cv: str,
                new_cv: str, initial_score: float) -> dict:
    """
    Runs the full Inner Reviewer stage: gathers hallucination, compatibility,
    and ATS-compliance data on new_cv, then calls Inner Reviewer to make a
    final PASS/FAIL call. On FAIL (or on a failed gate check), deletes new_cv
    and reruns the Rewrite CV step, then rechecks everything from the top.
    Capped at MAX_RETRIES; if still failing after that, returns a
    manual-review-needed result instead of looping forever.

    Args:
        model_flash: Model instance for the heavier steps (rewrite, verdict).
        model_flash_lite: Model instance for the lighter check steps.
        job_posting (str): The job posting text.
        base_cv (str): The candidate's original base CV text.
        new_cv (str): The current rewritten CV to review.
        initial_score (float): The original compatibility score (base_cv
            vs job_posting), from the very first Check Compatibility step.

    Returns:
        dict with keys:
            status: "approved" or "manual_review_needed"
            cv: the final CV text
            reason: (only on manual_review_needed) why it wasn't approved
    """
    retries = 0

    while True:
        # Gate 1: Hallucination check
        hallucination_result = hallucination_check.check_hallucination(
            model_flash_lite, base_cv, new_cv
        )
        if not hallucination_result["truthful"]:
            retries += 1
            if retries > MAX_RETRIES:
                return {
                    "status": "manual_review_needed",
                    "cv": new_cv,
                    "reason": f"Repeated hallucination failures: {hallucination_result['reasoning']}",
                }
            new_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv)
            continue

        # Gate 2: Compatibility comparison
        compat_result = compatibility_check.check_compatibility(
            model_flash_lite, job_posting, new_cv
        )
        new_score = compat_result["final_score"]
        if initial_score - new_score >= COMPATIBILITY_DROP_THRESHOLD:
            retries += 1
            if retries > MAX_RETRIES:
                return {
                    "status": "manual_review_needed",
                    "cv": new_cv,
                    "reason": (
                        f"Compatibility dropped {initial_score - new_score:.0f} "
                        f"points repeatedly (initial: {initial_score}, "
                        f"new: {new_score})"
                    ),
                }
            new_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv)
            continue

        # Check 3: ATS compliance (feeds into Inner Reviewer, no early exit)
        ats_result = ats_compliance_check.check_ats_compliance(model_flash_lite, new_cv)

        # Final synthesis: Inner Reviewer
        verdict = run_inner_reviewer(
            model_flash, hallucination_result, initial_score, new_score, ats_result
        )

        if verdict["verdict"] == "PASS":
            return {"status": "approved", "cv": new_cv}

        retries += 1
        if retries > MAX_RETRIES:
            return {
                "status": "manual_review_needed",
                "cv": new_cv,
                "reason": verdict["crucial_issue"],
            }
        new_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv)