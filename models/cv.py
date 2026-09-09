from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Experience:
    role: str
    employer: str
    dates: str
    location: Optional[str] = None
    bullets: List[str] = field(default_factory=list)


@dataclass
class Education:
    institution: str
    degree: str
    dates: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Project:
    name: str
    description: Optional[str] = None
    technologies: List[str] = field(default_factory=list)


@dataclass
class CV:
    name: str
    title: Optional[str] = None
    contact: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "contact": self.contact,
            "summary": self.summary,
            "experience": [
                {
                    "role": item.role,
                    "employer": item.employer,
                    "dates": item.dates,
                    "location": item.location,
                    "bullets": item.bullets,
                }
                for item in self.experience
            ],
            "education": [
                {
                    "institution": item.institution,
                    "degree": item.degree,
                    "dates": item.dates,
                    "location": item.location,
                }
                for item in self.education
            ],
            "skills": self.skills,
            "projects": [
                {
                    "name": item.name,
                    "description": item.description,
                    "technologies": item.technologies,
                }
                for item in self.projects
            ],
            "certifications": self.certifications,
        }