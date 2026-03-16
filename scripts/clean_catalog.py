"""
Script de nettoyage du catalogue académique EPL.

Objectif :
- Lire le fichier brut `data/raw/catalog_raw.csv` (fourni, séparateur `;`).
- Normaliser les colonnes et dériver :
    - department  : département (ex. "Genie civil", "Informatique et Systeme").
    - program     : libellé complet du programme (ex. "License Genie civile").
    - level       : niveau agrégé (L1, L2, L3, M1, M2) à partir du semestre + type (License/Master).
    - ue_code     : code d'UE synthétique par (programme, semestre).
    - ue_name     : nom d'UE synthétique.
    - subject_*   : code et nom de la matière (reprennent `code` et `intituler`).

Résultat :
- Écrit `data/processed/catalog_clean.csv`
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "catalog_raw.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "catalog_clean.csv"


def infer_department(license_str: str) -> str:
    """
    À partir du libellé `license` (ex. "License Genie civile"),
    isole grossièrement le département.
    """
    if not isinstance(license_str, str):
        return "Inconnu"
    # On enlève "License"/"Master" et on garde la suite
    parts = license_str.split()
    if not parts:
        return "Inconnu"
    if parts[0].lower() in {"license", "licence", "master"}:
        dept = " ".join(parts[1:])
    else:
        dept = license_str
    return dept.strip()


def infer_level(license_str: str, semestre) -> str:
    """
    Déduit un niveau agrégé (L1, L2, L3, M1, M2) à partir du type
    de diplôme et du semestre.
    """
    if pd.isna(semestre):
        # Si le semestre est manquant, on renvoie un niveau générique
        return "Lx" if isinstance(license_str, str) and license_str.lower().startswith("license") else "Mx"

    try:
        s = int(semestre)
    except (TypeError, ValueError):
        return "Lx" if isinstance(license_str, str) and license_str.lower().startswith("license") else "Mx"

    is_license = isinstance(license_str, str) and license_str.lower().startswith("license")

    if is_license:
        if s in (1, 2):
            return "L1"
        if s in (3, 4):
            return "L2"
        if s in (5, 6):
            return "L3"
        return "Lx"
    # Master
    if s in (1, 2):
        return "M1"
    if s in (3, 4):
        return "M2"
    return "Mx"


def short_program_code(license_str: str) -> str:
    """
    Crée un petit code programme (ex. "L-GC", "M-IS") pour construire un code d'UE.
    """
    if not isinstance(license_str, str) or not license_str:
        return "PRG"
    parts = license_str.split()
    level_prefix = "L" if parts[0].lower().startswith("lic") else "M"
    # Garder les initiales du reste ("Genie civile" -> "GC")
    initials = "".join(p[0].upper() for p in parts[1:] if p)
    return f"{level_prefix}-{initials or 'GEN'}"


def clean_catalog() -> pd.DataFrame:
    """Effectue le nettoyage du catalogue et renvoie le DataFrame nettoyé."""
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Fichier brut introuvable : {RAW_PATH}")

    df = pd.read_csv(RAW_PATH, sep=";")

    # Normalisation basique
    df.columns = [c.strip().lower() for c in df.columns]
    df["code"] = df["code"].astype(str).str.strip()
    df["intituler"] = df["intituler"].astype(str).str.strip()
    df["license"] = df["license"].astype(str).str.strip()

    # Conversion du semestre en nombre (peut contenir des valeurs manquantes)
    df["semestre"] = pd.to_numeric(df["semestre"], errors="coerce")

    # Département, programme, niveau
    df["program"] = df["license"]
    df["department"] = df["license"].apply(infer_department)
    df["level"] = df.apply(lambda row: infer_level(row["license"], row["semestre"]), axis=1)

    # Construction ue_code / ue_name synthétiques
    df["program_code"] = df["license"].apply(short_program_code)
    df["ue_code"] = df.apply(
        lambda row: f"{row['program_code']}-S{int(row['semestre']):02d}"
        if not pd.isna(row["semestre"])
        else f"{row['program_code']}-SXX",
        axis=1,
    )
    df["ue_name"] = df.apply(
        lambda row: f"UE Semestre {int(row['semestre'])} - {row['program']}"
        if not pd.isna(row["semestre"])
        else f"UE Hors semestre - {row['program']}",
        axis=1,
    )

    # Colonnes sujet
    df["subject_code"] = df["code"]
    df["subject_name"] = df["intituler"]

    # Colonnes de sortie dans l’ordre logique
    cleaned = df[
        [
            "ue_code",
            "ue_name",
            "subject_code",
            "subject_name",
            "credit",
            "semestre",
            "program",
            "department",
            "level",
        ]
    ].copy()

    # Nettoyage de base
    cleaned["credit"] = pd.to_numeric(cleaned["credit"], errors="coerce").fillna(0).astype(int)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_PATH, index=False)
    print(f"Catalogue nettoyé écrit dans : {OUTPUT_PATH}")
    return cleaned


if __name__ == "__main__":
    clean_catalog()







