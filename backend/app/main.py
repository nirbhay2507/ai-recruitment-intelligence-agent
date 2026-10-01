from pathlib import Path
import re

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="RecruitIntel AI",
    description="AI Recruitment Intelligence Agent",
    version="0.1.0"
)


# =========================================================
# MODELS
# =========================================================

class JobDescription(BaseModel):
    title: str
    description: str


class Candidate(BaseModel):
    name: str
    resume: str


class CandidateAnalysisRequest(BaseModel):
    job_title: str
    job_description: str
    resume: str


class MatchSkillsRequest(BaseModel):
    resume_skills: list[str]
    required_skills: list[str]


class RecruitRequest(BaseModel):
    job: JobDescription
    candidates: list[Candidate]


# =========================================================
# SKILLS
# =========================================================

SKILLS = [
    "python",
    "fastapi",
    "javascript",
    "typescript",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "aws",
    "git",
    "github",
    "react",
    "node.js",
    "django",
    "flask",
    "java",
    "c++",
    "pandas",
    "numpy",
    "machine learning",
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def extract_skills(text: str) -> list[str]:
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


def calculate_match(
    resume: str,
    required_skills: list[str]
):
    resume_lower = resume.lower()

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill.lower() in resume_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if len(required_skills) == 0:
        match_score = 0
    else:
        match_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

    return (
        matched_skills,
        missing_skills,
        round(match_score, 2)
    )


def get_recommendation(score: float) -> str:

    if score >= 80:
        return "Strong Match"

    elif score >= 60:
        return "Moderate Match"

    elif score >= 40:
        return "Partial Match"

    else:
        return "Low Match"


def extract_experience(resume: str) -> int:

    match = re.search(
        r"(\d+)\s*(?:\+)?\s*years?",
        resume.lower()
    )

    if match:
        return int(match.group(1))

    return 0


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to RecruitIntel AI",
        "status": "running",
        "version": "0.1.0"
    }


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard")
def dashboard():

    frontend_file = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "index.html"
    )

    if frontend_file.exists():
        return FileResponse(frontend_file)

    return {
        "error": "frontend/index.html not found"
    }


# =========================================================
# ANALYZE JOB DESCRIPTION
# =========================================================

@app.post("/analyze-jd")
def analyze_jd(job: JobDescription):

    required_skills = extract_skills(
        job.description
    )

    return {
        "job_title": job.title,
        "description": job.description,
        "required_skills": required_skills,
        "total_required_skills": len(required_skills)
    }


# =========================================================
# ANALYZE RESUME
# =========================================================

@app.post("/analyze-resume")
def analyze_resume(candidate: Candidate):

    skills = extract_skills(
        candidate.resume
    )

    experience_years = extract_experience(
        candidate.resume
    )

    return {
        "candidate": candidate.name,
        "experience_years": experience_years,
        "skills": skills,
        "total_skills": len(skills)
    }


# =========================================================
# MATCH SKILLS
# =========================================================

@app.post("/match-skills")
def match_skills(data: MatchSkillsRequest):

    resume_skills_lower = [
        skill.lower()
        for skill in data.resume_skills
    ]

    matched_skills = [
        skill
        for skill in data.required_skills
        if skill.lower() in resume_skills_lower
    ]

    missing_skills = [
        skill
        for skill in data.required_skills
        if skill.lower() not in resume_skills_lower
    ]

    if len(data.required_skills) == 0:
        match_score = 0
    else:
        match_score = (
            len(matched_skills)
            / len(data.required_skills)
        ) * 100

    return {
        "required_skills": data.required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": round(match_score, 2)
    }


# =========================================================
# ANALYZE CANDIDATE
# =========================================================

@app.post("/analyze-candidate")
def analyze_candidate(
    data: CandidateAnalysisRequest
):

    required_skills = extract_skills(
        data.job_description
    )

    resume_skills = extract_skills(
        data.resume
    )

    (
        matched_skills,
        missing_skills,
        match_score
    ) = calculate_match(
        data.resume,
        required_skills
    )

    recommendation = get_recommendation(
        match_score
    )

    experience_years = extract_experience(
        data.resume
    )

    return {
        "candidate": "Analyzed Candidate",
        "job_title": data.job_title,
        "experience_years": experience_years,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "recommendation": recommendation
    }


# =========================================================
# RANK CANDIDATES
# =========================================================

@app.post("/rank-candidates")
def rank_candidates(candidates: list[dict]):

    ranked = list(candidates)

    ranked.sort(
        key=lambda candidate: float(
            candidate.get("match_score", 0)
        ),
        reverse=True
    )

    for index, candidate in enumerate(
        ranked,
        start=1
    ):
        candidate["rank"] = index

    return {
        "total_candidates": len(ranked),
        "ranked_candidates": ranked
    }


# =========================================================
# COMPLETE RECRUITMENT PROCESS
# =========================================================

@app.post("/recruit")
def recruit(data: RecruitRequest):

    # -----------------------------------------------------
    # JOB SKILLS
    # -----------------------------------------------------

    required_skills = extract_skills(
        data.job.description
    )

    # -----------------------------------------------------
    # ANALYZE CANDIDATES
    # -----------------------------------------------------

    ranked_candidates = []

    for candidate in data.candidates:

        resume = candidate.resume

        (
            matched_skills,
            missing_skills,
            match_score
        ) = calculate_match(
            resume,
            required_skills
        )

        recommendation = get_recommendation(
            match_score
        )

        experience_years = extract_experience(
            resume
        )

        candidate_result = {

            "name": candidate.name,

            "resume": candidate.resume,

            "experience_years": experience_years,

            "resume_skills": extract_skills(
                candidate.resume
            ),

            "required_skills": required_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "match_score": match_score,

            "recommendation": recommendation
        }

        ranked_candidates.append(
            candidate_result
        )

    # -----------------------------------------------------
    # SORT BY MATCH SCORE
    # -----------------------------------------------------

    ranked_candidates.sort(
        key=lambda candidate:
            candidate["match_score"],
        reverse=True
    )

    # -----------------------------------------------------
    # ADD RANK
    # -----------------------------------------------------

    for index, candidate in enumerate(
        ranked_candidates,
        start=1
    ):

        candidate["rank"] = index

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {

        # IMPORTANT:
        # Send job title as STRING,
        # not an object.
        "job": data.job.title,

        "total_candidates": len(
            ranked_candidates
        ),

        "required_skills": required_skills,

        "ranked_candidates": ranked_candidates
    }