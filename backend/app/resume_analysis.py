import re

SKILLS = [
    "python", "fastapi", "django", "flask",
    "javascript", "typescript", "react",
    "node.js", "sql", "postgresql", "mysql",
    "mongodb", "docker", "kubernetes",
    "aws", "azure", "git", "github",
    "pandas", "numpy", "machine learning"
]


def extract_resume_info(text: str):
    text_lower = text.lower()

    skills = []

    for skill in SKILLS:
        if skill in text_lower:
            skills.append(skill)

    experience = 0

    match = re.search(
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?experience",
        text_lower
    )

    if match:
        experience = float(match.group(1))

    return {
        "skills": skills,
        "experience_years": experience,
        "resume_length": len(text)
    }