REQUIRED_SKILLS = {
    "python",
    "fastapi",
    "sql",
    "postgresql",
    "docker",
    "aws",
    "javascript",
    "typescript",
    "react"
}


def match_skills(resume_skills, job_skills):
    resume = {skill.lower() for skill in resume_skills}
    job = {skill.lower() for skill in job_skills}

    matched = sorted(resume & job)
    missing = sorted(job - resume)

    score = round((len(matched) / len(job)) * 100, 2) if job else 0

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }
    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }