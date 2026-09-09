import re
from py_simple import ask_ai
import steps.hallucination_check as hallucination_check
import steps.compatibility_check as compatibility_check
import steps.ats_compliance_check as ats_compliance_check
import steps.rewrite_cv as rewrite_cv

PROMPT_PATH = "prompts/inner_reviewer.md"
COMPATIBILITY_DROP_THRESHOLD = 25
MAX_RETRIES = 3  # separate counter for Stage A and Stage B


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


def load_verdict_prompt(hallucination_result: dict, initial_score: float,
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
    prompt = load_verdict_prompt(hallucination_result, initial_score, new_score, ats_result)
    response = ask_ai(model, prompt)
    response = normalize_response(response)
    return parse_verdict(response)


def run_checks(model_flash_lite, base_cv: str, new_cv: str, job_posting: str,
                initial_score: float) -> dict:
    """
    Runs the 3-check gate: hallucination, compatibility drop, ATS
    compliance. Returns whether the gate passed and everything Inner
    Reviewer will need if it did.
    """
    hallucination_result = hallucination_check.check_hallucination(
        model_flash_lite, base_cv, new_cv
    )
    if not hallucination_result["truthful"]:
        return {
            "passed": False,
            "reason": f"Hallucination check failed: {hallucination_result['reasoning']}",
        }

    compat_result = compatibility_check.check_compatibility(
        model_flash_lite, job_posting, new_cv
    )
    new_score = compat_result["final_score"]
    if initial_score - new_score >= COMPATIBILITY_DROP_THRESHOLD:
        return {
            "passed": False,
            "reason": (
                f"Compatibility dropped {initial_score - new_score:.0f} points "
                f"(initial: {initial_score}, new: {new_score})"
            ),
        }

    ats_result = ats_compliance_check.check_ats_compliance(model_flash_lite, new_cv)

    return {
        "passed": True,
        "hallucination_result": hallucination_result,
        "new_score": new_score,
        "ats_result": ats_result,
    }


def run_review(model_flash, model_flash_lite, job_posting: str, base_cv: str,
                initial_score: float) -> dict:
    """
    Runs the full Rewrite-Review loop (Stage A: blind rewrite, Stage B:
    targeted fix loop) as defined in REWRITE-REVIEW-LOOP.

    Stage A: rewrite from base_cv with no fix info. On a failed 3-check
    gate, discard the CV entirely and rewrite fresh again (capped at
    MAX_RETRIES). Once the gate passes, run Inner Reviewer. PASS -> done.
    FAIL -> move to Stage B carrying the flagged crucial issue.

    Stage B: rewrite from base_cv with the crucial issue to fix. On a
    failed 3-check gate, discard only the newest attempt (keep the last
    passing CV) and retry with the same fix instruction (capped at
    MAX_RETRIES, separate counter from Stage A). Once the gate passes,
    run Inner Reviewer. PASS -> done. FAIL -> loop back into Stage B
    with the newly flagged crucial issue.

    Args:
        model_flash: Model instance for the heavier steps (rewrite, verdict).
        model_flash_lite: Model instance for the lighter check steps.
        job_posting (str): The job posting text.
        base_cv (str): The candidate's original base CV text.
        initial_score (float): The original compatibility score (base_cv
            vs job_posting), from the very first Check Compatibility step.

    Returns:
        dict with keys:
            status: "approved" or "manual_review_needed"
            cv: the final CV text
            reason: (only on manual_review_needed) why it wasn't approved
    """
    # ---- STAGE A: blind rewrite loop ----
    stage_a_retries = 0
    new_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv)

    while True:
        checks = run_checks(model_flash_lite, base_cv, new_cv, job_posting, initial_score)

        if not checks["passed"]:
            stage_a_retries += 1
            if stage_a_retries > MAX_RETRIES:
                return {"status": "manual_review_needed", "cv": new_cv, "reason": checks["reason"]}
            new_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv)
            continue

        verdict = run_inner_reviewer(
            model_flash, checks["hallucination_result"], initial_score,
            checks["new_score"], checks["ats_result"]
        )
        if verdict["verdict"] == "PASS":
            return {"status": "approved", "cv": new_cv}

        # Inner Reviewer failed -> move into Stage B
        fix_instruction = verdict["crucial_issue"]
        last_passing_cv = new_cv
        break

    # ---- STAGE B: targeted fix loop ----
    stage_b_retries = 0

    while True:
        candidate_cv = rewrite_cv.rewrite_cv(model_flash, job_posting, base_cv, fix_instruction)
        checks = run_checks(model_flash_lite, base_cv, candidate_cv, job_posting, initial_score)

        if not checks["passed"]:
            stage_b_retries += 1
            if stage_b_retries > MAX_RETRIES:
                return {"status": "manual_review_needed", "cv": last_passing_cv, "reason": checks["reason"]}
            # discard only the newest attempt, keep last_passing_cv, retry same fix
            continue

        last_passing_cv = candidate_cv
        verdict = run_inner_reviewer(
            model_flash, checks["hallucination_result"], initial_score,
            checks["new_score"], checks["ats_result"]
        )
        if verdict["verdict"] == "PASS":
            return {"status": "approved", "cv": candidate_cv}

        fix_instruction = verdict["crucial_issue"]