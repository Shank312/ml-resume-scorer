

import os
from dotenv import load_dotenv

load_dotenv()

# API keys / config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # ← add this

# LLM settings
LLM_MODE = os.getenv("LLM_MODE", "relaxed").lower()  # "strict" or "relaxed"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
