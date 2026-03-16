"""
Simulation d'étudiants EPL à partir du catalogue nettoyé.

Objectif :
- Charger `data/processed/catalog_clean.csv`.
- Identifier les combinaisons (department, program, level).
- Générer > 1000 étudiants répartis sur **tous** les départements présents.

Sortie :
- `data/processed/students.csv` avec les colonnes :
    - student_id (STU0001, STU0002, …)
    - department
    - program
    - level
"""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "processed" / "catalog_clean.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "students.csv"


def generate_students(total_students: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """Génère un ensemble d'étudiants répartis sur tous les départements."""
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Catalogue nettoyé introuvable : {CATALOG_PATH} "
            f"(exécute d'abord scripts/clean_catalog.py)"
        )

    catalog = pd.read_csv(CATALOG_PATH)

    # On n'utilise que les lignes avec un semestre défini
    catalog = catalog.dropna(subset=["semestre"])

    # Combinaisons uniques department/program/level
    combos = (
        catalog[["department", "program", "level"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if combos.empty:
        raise ValueError("Aucune combinaison (department, program, level) trouvée dans le catalogue.")

    rng = np.random.default_rng(random_state)

    # Répartition approximativement uniforme des étudiants sur les combinaisons
    n_combos = len(combos)
    base = total_students // n_combos
    remainder = total_students % n_combos

    students_rows = []
    student_counter = 1

    for idx, row in combos.iterrows():
        n = base + (1 if idx < remainder else 0)
        for _ in range(n):
            student_id = f"STU{student_counter:04d}"
            students_rows.append(
                {
                    "student_id": student_id,
                    "department": row["department"],
                    "program": row["program"],
                    "level": row["level"],
                }
            )
            student_counter += 1

    students = pd.DataFrame(students_rows)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    students.to_csv(OUTPUT_PATH, index=False)
    print(f"{len(students)} étudiants simulés écrits dans : {OUTPUT_PATH}")
    print("Départements présents :", ", ".join(sorted(students['department'].unique())))

    return students


if __name__ == "__main__":
    generate_students()







