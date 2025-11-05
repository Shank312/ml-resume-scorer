

import os, re, json, logging
from typing import Dict, List, Tuple
from ..config import OPENAI_API_KEY, LLM_MODE, LLM_MODEL
from .prompts import STRICT_PROMPT, RELAXED_PROMPT

log = logging.getLogger("llm")
if not log.handlers:
    # very small console handler (avoid duplicate handlers on reload)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    log.addHandler(h)
log.setLevel(logging.WARNING)


def _overlap_ratio(a: List[str], b: List[str]) -> float:
    sa, sb = set(x.lower() for x in a), set(x.lower() for x in b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    return inter / max(len(sa), len(sb))


def _flatten_repo_libs(repo_lib_usage: Dict[str, List[str]]) -> List[str]:
    libs = []
    for _, lst in (repo_lib_usage or {}).items():
        libs.extend(lst or [])
    return sorted(set(libs))


def _engineer_heuristic(resume_signals: Dict[str, List[str]],
                        repo_lib_usage: Dict[str, List[str]]) -> float:
    """
    0..1 heuristic:
    - checks resume↔github lib overlap
    - gives points for MLOps/deploy libs
    """
    resume_libs = sorted(set(sum((v for v in (resume_signals or {}).values()), [])))
    gh_libs = _flatten_repo_libs(repo_lib_usage)

    overlap = _overlap_ratio(resume_libs, gh_libs)

    # ML engineering signals in repos
    mlops_signals = {"mlflow", "docker", "dvc", "prefect", "airflow"}
    deploy_signals = {"fastapi", "flask", "streamlit", "onnx"}
    dl_signals = {"torch", "pytorch", "tensorflow", "tf", "keras"}
    classic_ml = {"scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost"}

    s_mlops = bool(set(gh_libs) & mlops_signals)
    s_deploy = bool(set(gh_libs) & deploy_signals)
    s_dl = bool(set(gh_libs) & dl_signals)
    s_classic = bool(set(gh_libs) & classic_ml)

    score = 0.4 * overlap
    score += 0.2 if s_mlops else 0.0
    score += 0.2 if s_deploy else 0.0
    score += 0.1 if s_dl else 0.0
    score += 0.1 if s_classic else 0.0
    return min(1.0, score)


def _extract_json_block(text: str) -> str | None:
    """
    Try to extract a single JSON object from arbitrary LLM output.
    """
    if not text:
        return None
    # First, naive strict parse
    try:
        json.loads(text)
        return text
    except Exception:
        pass
    # Then, find the outermost {...} block
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        candidate = m.group(0)
        # try to minimally sanitize smart quotes
        candidate = candidate.replace("“", "\"").replace("”", "\"").replace("’", "'")
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            return candidate  # still return; caller will attempt softer parsing
    return None


def llm_score_boost(resume_text: str,
                    projects: List[str],
                    resume_signals: Dict[str, List[str]],
                    repo_lib_usage: Dict[str, List[str]]) -> Tuple[float, str | None]:
    """
    Returns: (bonus_norm_0_to_1, rationale_str)
    - Combines a deterministic heuristic pre-score with an LLM judgment.
    - If no API key or API fails → returns (heuristic*0.5, None) for stability.
    """
    # Heuristic pre-boost
    heur = _engineer_heuristic(resume_signals, repo_lib_usage)  # 0..1

    if not OPENAI_API_KEY:
        log.warning("LLM bonus: OPENAI_API_KEY missing; returning heuristic*0.5")
        return round(0.5 * heur, 3), None

    model = LLM_MODEL or "gpt-4.1-mini"
    mode_prompt = STRICT_PROMPT if (LLM_MODE or "relaxed").lower() == "strict" else RELAXED_PROMPT

    # build structured summary (small)
    summary = {
        "projects_sample": (projects or [])[:8],
        "resume_signals": resume_signals or {},
        "repo_lib_usage_sample": dict(list((repo_lib_usage or {}).items())[:8]),
    }

    prompt = f"""{mode_prompt}

Heuristic pre-score (0..1): {round(heur, 3)}
Resume snippet (truncated to ~6k chars):
{(resume_text or "")[:6000]}

Structured evidence:
{json.dumps(summary, ensure_ascii=False)}
"""

    try:
        # lazy import so app runs without openai if key missing
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Make the chat completion call
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=180,
        )

        content = (completion.choices[0].message.content or "").strip()

        # Try robust JSON extraction
        json_block = _extract_json_block(content) or ""
        bonus_norm = None
        rationale = None

        try:
            data = json.loads(json_block)
            bonus = int(data.get("bonus_points_0_to_10", int(round(10 * heur * 0.5))))
            rationale = data.get("rationale")
            bonus = min(max(bonus, 0), 10)
            bonus_norm = bonus / 10.0
        except Exception:
            # last-resort regex parsing
            m = re.search(r'"bonus_points_0_to_10"\s*:\s*(\d+)', content)
            bonus = int(m.group(1)) if m else int(round(10 * heur * 0.5))
            rat_m = re.search(r'"rationale"\s*:\s*"([^"]+)"', content.replace("\n", " "))
            rationale = rat_m.group(1) if rat_m else None
            bonus = min(max(bonus, 0), 10)
            bonus_norm = bonus / 10.0

        # trim rationale a bit to keep payload small
        if rationale and len(rationale) > 400:
            rationale = rationale[:397] + "..."

        return float(bonus_norm), rationale

    except Exception as e:
        log.warning("LLM bonus: exception: %s", str(e)[:200])
        # API/network error → half of heuristic
        return round(0.5 * heur, 3), None
