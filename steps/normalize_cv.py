import json

from models.cv import CV, Experience, Education, Project
from py_simple import ask_ai


PROMPT_PATH = "prompts/normalize_cv.md"


def _response_to_text(response) -> str:
    """Convert ask_ai() output into plain text."""
    if isinstance(response, str):
        return response

    if isinstance(response, list):
        parts = []

        for item in response:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])

        return "\n".join(parts)

    raise TypeError(
        f"Unexpected response type from ask_ai: {type(response)}"
    )


def _strip_json_fences(response: str) -> str:
    """Remove markdown JSON fences if the model added them."""
    response = response.strip()

    if response.startswith("```json"):
        response = response[len("```json"):].strip()

    elif response.startswith("```"):
        response = response[len("```"):].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def normalize_cv(model, base_cv_text: str) -> CV:
    """
    Normalize extracted CV text into the canonical CV structure.

    This does not rewrite the CV. It only identifies and organizes
    the information already present in the source CV.
    """

    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.replace("{base_cv}", base_cv_text)

    response = ask_ai(model, prompt)
    response = _response_to_text(response)
    response = _strip_json_fences(response)

    data = json.loads(response)

    experience = [
        Experience(
            role=item.get("role", ""),
            employer=item.get("employer", ""),
            dates=item.get("dates", ""),
            location=item.get("location"),
            bullets=item.get("bullets", []),
        )
        for item in data.get("experience", [])
    ]

    education = [
        Education(
            institution=item.get("institution", ""),
            degree=item.get("degree", ""),
            dates=item.get("dates"),
            location=item.get("location"),
        )
        for item in data.get("education", [])
    ]

    projects = [
        Project(
            name=item.get("name", ""),
            description=item.get("description"),
            technologies=item.get("technologies", []),
        )
        for item in data.get("projects", [])
    ]

    return CV(
        name=data.get("name", ""),
        title=data.get("title"),
        contact=data.get("contact", []),
        summary=data.get("summary"),
        experience=experience,
        education=education,
        skills=data.get("skills", []),
        projects=projects,
        certifications=data.get("certifications", []),
    )


def cv_to_text(cv: CV) -> str:
    """
    Convert the canonical CV structure into deterministic plain text.

    This is the boundary between normalization and the existing
    rewrite/review pipeline, which currently expects a string.
    """

    sections = []

    sections.append(cv.name)

    if cv.title:
        sections.append(cv.title)

    if cv.contact:
        sections.extend(cv.contact)

    if cv.summary:
        sections.append("")
        sections.append("SUMMARY")
        sections.append(cv.summary)

    if cv.experience:
        sections.append("")
        sections.append("WORK EXPERIENCE")

        for item in cv.experience:
            sections.append(item.role)
            sections.append(item.employer)

            if item.location:
                sections.append(item.location)

            sections.append(item.dates)

            for bullet in item.bullets:
                sections.append(f"- {bullet}")

    if cv.education:
        sections.append("")
        sections.append("EDUCATION")

        for item in cv.education:
            sections.append(item.degree)
            sections.append(item.institution)

            if item.location:
                sections.append(item.location)

            if item.dates:
                sections.append(item.dates)

    if cv.skills:
        sections.append("")
        sections.append("SKILLS")
        sections.extend(f"- {skill}" for skill in cv.skills)

    if cv.projects:
        sections.append("")
        sections.append("PROJECTS")

        for project in cv.projects:
            sections.append(project.name)

            if project.description:
                sections.append(project.description)

            if project.technologies:
                sections.append(
                    f"Technologies: {', '.join(project.technologies)}"
                )

    if cv.certifications:
        sections.append("")
        sections.append("CERTIFICATIONS")
        sections.extend(
            f"- {certification}"
            for certification in cv.certifications
        )

    return "\n".join(
        str(section)
        for section in sections
        if section is not None
    ).strip()