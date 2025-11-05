

import re
from typing import Dict, List
from ..scoring.skill_matrix import ML_SKILL_MATRIX

def find_ml_keywords(text: str) -> Dict[str, List[str]]:
    text_low = text.lower()
    found = {}
    for cat, keys in ML_SKILL_MATRIX.items():
        hits = []
        for k in keys:
            # match whole words or common import patterns
            pattern = r"(?:^|[^a-z])" + re.escape(k.lower()) + r"(?:[^a-z]|$)"
            if re.search(pattern, text_low):
                hits.append(k)
        if hits:
            found[cat] = sorted(list(set(hits)))
    return found


def infer_projects(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    projects = []

    # very broad triggers
    triggers = [
        "project", "classifier", "detection", "regression", "segmentation",
        "forecast", "forecasting", "fine-tune", "finetune", "nlp", "vision",
        "deploy", "inference", "pipeline", "training", "streamlit", "api"
    ]

    for l in lines:
        low = l.lower()
        # bullet or numbered lines or trigger keywords
        if l.startswith(("•", "-", "*")) or any(t in low for t in triggers):
            if 8 <= len(l) <= 200:
                projects.append(l[:200])

    # remove duplicates while preserving order
    seen = set()
    uniq = []
    for p in projects:
        if p not in seen:
            uniq.append(p)
            seen.add(p)

    return uniq[:12]   # return top 12 unique project lines


def detect_education_signals(text: str) -> bool:
    t = text.lower()

    edu_keywords = [
        "b.tech", "btech", "m.tech", "mtech",
        "b.sc", "bsc", "m.sc", "msc",
        "b.e", "be", "m.e", "me",     # added most common BE/ME
        "coursera", "udemy", "deeplearning.ai", "fast.ai",
        "andrew ng", "specialization", "nanodegree"
    ]

    return any(s in t for s in edu_keywords)
