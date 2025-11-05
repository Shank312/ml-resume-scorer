

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ScoreEvidence(BaseModel):
    github_repos_count: int = 0
    ml_libs_detected: List[str] = []
    projects_found: List[str] = []
    repo_lib_usage: Dict[str, List[str]] = {}
    resume_signals: Dict[str, List[str]] = {}
    llm_rationale: Optional[str] = None   # ← add this

class ScoreResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    level: str
    evidence: ScoreEvidence

class ScoreRequest(BaseModel):
    github_url: Optional[str] = None
    resume_text_override: Optional[str] = None  # if you want to paste raw text instead of PDF
