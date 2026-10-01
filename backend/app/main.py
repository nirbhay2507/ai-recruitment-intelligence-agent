from fastapi import FastAPI
from pydantic import BaseModel
import re
from backend.app.resume_analysis import extract_resume_info
from backend.app.skill_matching import match_skills
class Candidate(BaseModel):
    name: str
    match_score: float
from .candidate_ranking import rank_candidates

app = FastAPI(
    title="RecruitIntel AI",
    description="AI Recruitment Intelligence Agent",
    version="0.1.0"
)


class JobDescription(BaseModel):
    title: str
    description: str
class Candidate(BaseModel):
    name: str
    resume: str
class RecruitRequest(BaseModel):
    job: JobDescription
    candidates: list    


# Skills we currently recognize
SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "fastapi",
    "django",
    "flask",
    "react",
    "node.js",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "git",
    "github",
    "rest api",
    "machine learning",
    "pandas",
    "numpy",
]


def find_skills(text: str):
    text_lower = text.lower()

    found = []

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)

    return found


def extract_experience(text: str):
    patterns = [
        r"(\d+)\+?\s*(?:years|year|yrs|yr)\s*(?:of)?\s*experience",
        r"experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|year)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())

        if match:
            return int(match.group(1))

    return 0


@app.get("/")
def root():
    return {
        "project": "RecruitIntel AI",
        "message": "AI Recruitment Intelligence Agent is running!"
    }


@app.post("/analyze-jd")
def analyze_jd(job: JobDescription):

    text = f"{job.title} {job.description}"

    skills = find_skills(text)

    experience = extract_experience(job.description)

    required_skills = []
    preferred_skills = []

    description_lower = job.description.lower()

    for skill in skills:

        skill_lower = skill.lower()

        if (
            f"{skill_lower} is preferred" in description_lower
            or f"{skill_lower} preferred" in description_lower
            or f"{skill_lower} is a plus" in description_lower
            or f"{skill_lower} nice to have" in description_lower
        ):
            preferred_skills.append(skill)

        else:
            required_skills.append(skill)

    return {
        "job_title": job.title,

        "experience_required": experience,

        "required_skills": required_skills,

        "preferred_skills": preferred_skills,

        "analysis": {
            "skills_detected": len(skills),
            "experience_detected": experience > 0
        },

        "next_agent": "Resume Analysis Agent"
    }
class ResumeText(BaseModel):
    text: str


@app.post("/analyze-resume")
def analyze_resume(resume: ResumeText):
    return extract_resume_info(resume.text)

class SkillMatchRequest(BaseModel):
    resume_skills: list[str]
    job_skills: list[str]


@app.post("/match-skills")
def match_resume_skills(data: SkillMatchRequest):
    return match_skills(
        data.resume_skills,
        data.job_skills
    )

class CandidateAnalysisRequest(BaseModel):
    job_title: str
    job_description: str
    resume_text: str


@app.post("/analyze-candidate")
def analyze_candidate(data: CandidateAnalysisRequest):

    # 1. Analyze Job Description
    jd_result = analyze_jd(
        JobDescription(
            title=data.job_title,
            description=data.job_description
        )
    )

    # 2. Analyze Resume
    resume_result = extract_resume_info(data.resume_text)

    # 3. Match skills
    skill_result = match_skills(
        resume_result["skills"],
        jd_result["required_skills"]
    )

    # 4. Final candidate score
    match_score = skill_result["match_score"]

    if match_score >= 80:
        recommendation = "Strong Match"
    elif match_score >= 60:
        recommendation = "Moderate Match"
    else:
        recommendation = "Low Match"

    return {
        "candidate": "Analyzed Candidate",
        "job_title": data.job_title,
        "experience_years": resume_result["experience_years"],
        "resume_skills": resume_result["skills"],
        "required_skills": jd_result["required_skills"],
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "match_score": match_score,
        "recommendation": recommendation
    }
@app.post("/rank-candidates")
def rank_candidate_list(candidates: list[Candidate]):
    ranked = sorted(
        candidates,
        key=lambda x: x.match_score,
        reverse=True
    )

    return {
        "total_candidates": len(ranked),
        "ranked_candidates": ranked
    }
@app.post("/recruit")
def recruit(data: RecruitRequest):

    required_skills = [
        "python",
        "fastapi",
        "sql",
        "postgresql",
        "docker",
        "aws"
    ]

    ranked_candidates = []

    for candidate in data.candidates:

        resume = candidate.resume.lower()

        matched_skills = []

        for skill in required_skills:
            if skill in resume:
                matched_skills.append(skill)

        score = (
            len(matched_skills) / len(required_skills)
        ) * 100

        ranked_candidates.append({
            "name": candidate.name,
            "resume": candidate.resume,
            "matched_skills": matched_skills,
            "match_score": round(score, 2)
        })

    ranked_candidates.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "job": data.job.title,
        "total_candidates": len(ranked_candidates),
        "ranked_candidates": ranked_candidates
    }
    # Highest score first
    ranked_candidates.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )


    return {

        "job": job_title,

        "total_candidates": len(ranked_candidates),

        "ranked_candidates": ranked_candidates

    }
def recruit(data: RecruitRequest):
    ranked = rank_candidates(data.candidates)

    return {
        "job": data.job.title,
        "total_candidates": len(ranked),
        "ranked_candidates": ranked
    }
from fastapi.responses import FileResponse

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/index.html")