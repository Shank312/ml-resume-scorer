

import httpx
from typing import Dict, List
from ..config import GITHUB_TOKEN
from ..scoring.skill_matrix import ML_SKILL_MATRIX

def _headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def parse_owner_repo(github_url: str):
    # supports https://github.com/<owner> or /<owner>?tab=repositories etc.
    parts = github_url.strip("/").split("/")
    if "github.com" in parts:
        idx = parts.index("github.com")
        parts = parts[idx+1:]
    owner = parts[0] if parts else ""
    return owner

async def fetch_repos(owner: str, max_repos: int = 25) -> List[Dict]:
    url = f"https://api.github.com/users/{owner}/repos?per_page={max_repos}&sort=updated"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=_headers())
        r.raise_for_status()
        return r.json()

async def fetch_repo_readme(owner: str, repo: str) -> str:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        return r.text if r.status_code == 200 else ""

def scan_libs_in_text(text: str) -> List[str]:
    text_low = text.lower()
    hits = set()
    for keys in ML_SKILL_MATRIX.values():
        for k in keys:
            if k.lower() in text_low:
                hits.add(k)
    return sorted(hits)

async def analyze_github(github_url: str) -> Dict:
    owner = parse_owner_repo(github_url)
    if not owner:
        return {"repos": [], "repo_lib_usage": {}, "libs_detected": []}

    repos = await fetch_repos(owner)
    repo_lib_usage = {}
    all_hits = set()
    for r in repos:
        name = r.get("name","")
        readme = await fetch_repo_readme(owner, name)
        libs = scan_libs_in_text(readme)
        if libs:
            repo_lib_usage[name] = libs
            all_hits.update(libs)

    return {
        "repos": repos,
        "repo_lib_usage": repo_lib_usage,
        "libs_detected": sorted(all_hits)
    }
