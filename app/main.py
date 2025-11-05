

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .schemas import ScoreRequest, ScoreResponse, ScoreEvidence
from .extract.pdf_reader import extract_text_from_pdf_bytes
from .extract.resume_parser import find_ml_keywords, infer_projects, detect_education_signals
from .sources.github_analyzer import analyze_github
from .scoring.scorer import score_resume, score_github, final_score, to_level
from .llm.llm_client import llm_score_boost  # ← LLM bonus

app = FastAPI(title="ML Resume Scorer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok"}

# -------- PDF (multipart/form-data) ----------
@app.post("/score/pdf", response_model=ScoreResponse)
async def score_pdf_endpoint(
    resume_pdf: UploadFile = File(...),
    github_url: Optional[str] = Form(None),
):
    if "pdf" not in (resume_pdf.content_type or ""):
        raise HTTPException(status_code=400, detail="resume_pdf must be a PDF")

    pdf_bytes = await resume_pdf.read()
    resume_text = extract_text_from_pdf_bytes(pdf_bytes)

    # parse resume signals
    resume_signals = find_ml_keywords(resume_text)
    projects = infer_projects(resume_text)
    edu_flag = detect_education_signals(resume_text)

    # analyze github (optional)
    gh_result = {"repos": [], "repo_lib_usage": {}, "libs_detected": []}
    if github_url:
        gh_result = await analyze_github(github_url)

    # scoring components
    resume_component = score_resume(resume_signals, projects, edu_flag)
    github_component = score_github(gh_result["repo_lib_usage"], len(gh_result["repos"]))

    # LLM bonus (+0..10 points) with rationale
    llm_bonus_norm, llm_rationale = llm_score_boost(
        resume_text=resume_text,
        projects=projects,
        resume_signals=resume_signals,
        repo_lib_usage=gh_result["repo_lib_usage"]
    )

    score_int = final_score(resume_component, github_component, llm_bonus=llm_bonus_norm)
    level = to_level(score_int)

    evidence = ScoreEvidence(
        github_repos_count=len(gh_result["repos"]),
        ml_libs_detected=sorted(set(gh_result["libs_detected"]) | set(sum(resume_signals.values(), []))),
        projects_found=projects[:8],
        repo_lib_usage=gh_result["repo_lib_usage"],
        resume_signals=resume_signals,
        llm_rationale=llm_rationale,  # ← include rationale
    )
    return ScoreResponse(score=score_int, level=level, evidence=evidence)

# -------- JSON (application/json) ----------
@app.post("/score/json", response_model=ScoreResponse)
async def score_json_endpoint(
    github_url: Optional[str] = None,  # pass as query param
    body: ScoreRequest = Body(...)
):
    if not body.resume_text_override:
        raise HTTPException(status_code=400, detail="resume_text_override is required for JSON endpoint")

    resume_text = body.resume_text_override

    # parse resume signals
    resume_signals = find_ml_keywords(resume_text)
    projects = infer_projects(resume_text)
    edu_flag = detect_education_signals(resume_text)

    # analyze github (optional)
    gh_result = {"repos": [], "repo_lib_usage": {}, "libs_detected": []}
    if github_url:
        gh_result = await analyze_github(github_url)

    # scoring components
    resume_component = score_resume(resume_signals, projects, edu_flag)
    github_component = score_github(gh_result["repo_lib_usage"], len(gh_result["repos"]))

    # LLM bonus (+0..10 points) with rationale
    llm_bonus_norm, llm_rationale = llm_score_boost(
        resume_text=resume_text,
        projects=projects,
        resume_signals=resume_signals,
        repo_lib_usage=gh_result["repo_lib_usage"]
    )

    score_int = final_score(resume_component, github_component, llm_bonus=llm_bonus_norm)
    level = to_level(score_int)

    evidence = ScoreEvidence(
        github_repos_count=len(gh_result["repos"]),
        ml_libs_detected=sorted(set(gh_result["libs_detected"]) | set(sum(resume_signals.values(), []))),
        projects_found=projects[:8],
        repo_lib_usage=gh_result["repo_lib_usage"],
        resume_signals=resume_signals,
        llm_rationale=llm_rationale,  # ← include rationale
    )
    return ScoreResponse(score=score_int, level=level, evidence=evidence)
