

from typing import Dict, List
from .skill_matrix import WEIGHTS, LEVELS
from ..llm.llm_client import llm_score_boost  # (kept; not used here directly but OK)

def _cap(x, lo=0, hi=1):
    return max(lo, min(hi, x))

def score_resume(resume_signals: Dict[str, List[str]], projects: List[str], education_flag: bool) -> float:
    # very simple: number of categories hit
    cats = len(resume_signals)
    resume_lib_strength = _cap(cats / 6)  # normalize roughly
    projects_strength = _cap(len(projects) / 5)
    edu_strength = 1.0 if education_flag else 0.0

    return (
        WEIGHTS["libs_detected"] * resume_lib_strength +
        WEIGHTS["projects_in_resume"] * projects_strength +
        WEIGHTS["education_courses"] * edu_strength
    )

def score_github(repo_lib_usage: Dict[str, List[str]], total_repos: int) -> float:
    portfolio_depth = _cap(len(repo_lib_usage) / max(3, total_repos or 1))  # repos with ML libs
    proof_strength = _cap(len(repo_lib_usage) / 5)  # 5 repos with libs = max
    return (
        WEIGHTS["portfolio_depth"] * portfolio_depth +
        WEIGHTS["github_proof"] * proof_strength
    )

def to_level(score_int: int) -> str:
    for thresh, label in LEVELS:
        if score_int >= thresh:
            return label
    return "Beginner"

def final_score(resume_component: float, github_component: float, llm_bonus: float = 0.0) -> int:
    # llm_bonus is 0..1 → up to +10 points
    raw = resume_component + github_component + 0.10 * _cap(llm_bonus)
    return int(round(_cap(raw, 0, 1) * 100))
