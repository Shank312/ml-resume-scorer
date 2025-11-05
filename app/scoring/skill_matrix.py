

ML_SKILL_MATRIX = {
    "python_data_stack": ["numpy", "pandas", "scipy", "matplotlib", "seaborn", "polars"],
    "classical_ml": ["scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost"],
    "deep_learning": ["pytorch", "torch", "tensorflow", "tf", "keras"],
    "mlops": ["mlflow", "dvc", "wandb", "onnx", "docker"],
    "deployment": ["fastapi", "flask", "gradio", "streamlit"],
    "data_storage": ["sql", "postgresql", "mysql", "mongodb", "snowflake", "bigquery"],
    "cv_nlp": ["opencv", "transformers", "spacy", "nltk", "huggingface"],
}

WEIGHTS = {
    "github_proof": 0.35,
    "libs_detected": 0.20,
    "projects_in_resume": 0.20,
    "portfolio_depth": 0.15,   # e.g., multiple repos with real code
    "education_courses": 0.10, # simple heuristic for now
}

LEVELS = [
    (85, "Strong ML Practitioner"),
    (70, "Solid ML Engineer"),
    (55, "Developing"),
    (0,  "Beginner"),
]
