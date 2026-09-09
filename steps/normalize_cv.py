import json

from models.cv import CV, Experience, Education, Project
from py_simple import ask_ai


def normalize_cv(base_cv_text: str) -> CV:
    """
    Convert extracted CV text into the project's canonical CV structure.

    This step normalizes semantics only. It does not rewrite CV content.
    """

    with open("prompts/normalize_cv.md", "r", encoding="utf-8") as file:
        prompt = file.read()

    prompt = prompt.replace("{base_cv}", base_cv_text)

    response = ask_ai(prompt)

    # Handle models that wrap JSON in markdown fences.
    response = response.strip()

    if response.startswith("```"):
        response = response.split("\n", 1)[1]
        response = response.rsplit("```", 1)[0].strip()

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