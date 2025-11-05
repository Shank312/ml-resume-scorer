# ML Resume Scorer

AI powered Resume Screening System that scores a candidate’s resume based on job description fit.  
This tool helps recruiters & hiring teams instantly identify the most relevant profiles.

---

## 🚀 Features

- Upload resume (PDF / text)
- Upload / paste Job Description
- ML model extracts skills, experience and keywords
- Generates score (0–100) + reasoning
- Identifies gaps between JD & Resume
- FastAPI backend (REST API)
- Ready to deploy on Render / Railway / AWS / GCP / Azure

---

## 🧠 Tech Stack

| Component  | Tech |
|-----------|------|
| Backend   | FastAPI |
| Model     | NLP + ML |
| Parsing   | PyPDF2 / SpaCy |
| Frontend  | (optional) FastAPI Swagger UI |
| Deploy    | Render / Railway |

---

## 📁 Project Structure

ml-resume-scorer/
├─ app/
│ ├─ main.py
│ ├─ model.py
│ ├─ scorer.py
│ └─ utils.py
├─ requirements.txt
├─ .gitignore
├─ .gitattributes
└─ README.md


> `venv`, `env`, caches are ignored (not committed)

---

## ⚙️ Setup (Local Run)

```bash
git clone https://github.com/Shank312/ml-resume-scorer.git
cd ml-resume-scorer

python -m venv .venv
source .venv/Scripts/activate   # Windows

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

API Docs automatically available →
http://localhost:8080/docs


📝 Usage

Send Resume + Job Description → get resume score.


🏗 Future Roadmap

Build UI Dashboard

Add ATS format checker

Add skill-gap recommender

Integrate with LinkedIn profile scraping


⭐ Contribute

PRs are welcome!


📄 License

MIT License
