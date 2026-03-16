"""
Simulation des notes des étudiants EPL.

Objectif :
- Charger :
    - `data/processed/catalog_clean.csv`
    - `data/processed/students.csv`
- Pour chaque étudiant, générer des notes dans les matières de son programme/niveau.

Sortie principale :
- `data/processed/notes_epl.csv` avec les colonnes :
    - student_id
    - department
    - program
    - level
    - ue_code
    - ue_name
    - subject_code
    - subject_name
    - teacher
    - credit
    - grade  (sur 20)
"""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "processed" / "catalog_clean.csv"
STUDENTS_PATH = ROOT / "data" / "processed" / "students.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "notes_epl.csv"


TEACHERS_BY_DEPT = {
    "Genie civile": ["Dr GC1", "Dr GC2", "Pr GC3"],
    "Genie Electrique": ["Dr GE1", "Dr GE2", "Pr GE3"],
    "Genie Mecanique": ["Dr GM1", "Dr GM2", "Pr GM3"],
    "Informatique et Systeme": ["Dr IS1", "Dr IS2", "Pr IS3"],
    "Intelligence Artificielle et Big Data": ["Dr IA1", "Dr IA2", "Pr IA3"],
    "Logistique et Transport": ["Dr LT1", "Dr LT2", "Pr LT3"],
}


def choose_teacher(department: str, rng: np.random.Generator) -> str:
    """Choisit un enseignant plausible pour un département donné."""
    for key, names in TEACHERS_BY_DEPT.items():
        if key.lower() in str(department).lower():
            return rng.choice(names).item()
    # Département inconnu -> enseignant générique
    return rng.choice(["Dr X", "Dr Y", "Pr Z"]).item()


def simulate_grade(rng: np.random.Generator, mean: float = 11.0, std: float = 3.0) -> float:
    """
    Simule une note sur 20 ~ N(mean, std^2), tronquée à [0, 20].
    """
    grade = rng.normal(loc=mean, scale=std)
    grade = max(0.0, min(20.0, float(grade)))
    return round(grade, 2)


def generate_grades(random_state: int = 123) -> pd.DataFrame:
    """Génère le dataset principal de notes EPL."""
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Catalogue nettoyé introuvable : {CATALOG_PATH} "
            f"(exécute d'abord scripts/clean_catalog.py)"
        )
    if not STUDENTS_PATH.exists():
        raise FileNotFoundError(
            f"Fichier étudiants introuvable : {STUDENTS_PATH} "
            f"(exécute d'abord scripts/generate_students.py)"
        )

    catalog = pd.read_csv(CATALOG_PATH)
    students = pd.read_csv(STUDENTS_PATH)

    # On ignore les matières sans semestre
    catalog = catalog.dropna(subset=["semestre"])

    rng = np.random.default_rng(random_state)

    notes_rows = []

    # Pour l'efficacité, on indexe le catalogue par (program, level)
    grouped_catalog = catalog.groupby(["program", "level"])

    for _, stu in students.iterrows():
        key = (stu["program"], stu["level"])
        if key not in grouped_catalog.groups:
            # Si on ne trouve pas exactement le couple, on tente par programme seul
            cat_subset = catalog[catalog["program"] == stu["program"]]
        else:
            cat_subset = grouped_catalog.get_group(key)

        if cat_subset.empty:
            # Aucun cours trouvé pour cet étudiant -> on saute
            continue

        # Option : tous les cours du programme & niveau
        for _, row in cat_subset.iterrows():
            teacher = choose_teacher(stu["department"], rng)
            grade = simulate_grade(rng)

            notes_rows.append(
                {
                    "student_id": stu["student_id"],
                    "department": stu["department"],
                    "program": stu["program"],
                    "level": stu["level"],
                    "ue_code": row["ue_code"],
                    "ue_name": row["ue_name"],
                    "subject_code": row["subject_code"],
                    "subject_name": row["subject_name"],
                    "teacher": teacher,
                    "credit": int(row["credit"]),
                    "grade": grade,
                }
            )

    notes = pd.DataFrame(notes_rows)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    notes.to_csv(OUTPUT_PATH, index=False)
    print(f"{len(notes)} lignes de notes simulées écrites dans : {OUTPUT_PATH}")

    return notes


if __name__ == "__main__":
    generate_grades()







