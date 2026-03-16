"""
Fonctions utilitaires pour charger les différents CSV du projet.
"""

from pathlib import Path
from functools import lru_cache

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"


def _ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")


@lru_cache(maxsize=1)
def load_catalog() -> pd.DataFrame:
    """Charge le catalogue nettoyé."""
    path = DATA_DIR / "catalog_clean.csv"
    _ensure_exists(path)
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_students() -> pd.DataFrame:
    """Charge la table des étudiants simulés."""
    path = DATA_DIR / "students.csv"
    _ensure_exists(path)
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_notes() -> pd.DataFrame:
    """Charge le dataset principal des notes."""
    path = DATA_DIR / "notes_epl.csv"
    _ensure_exists(path)
    df = pd.read_csv(path)
    # S'assurer que la colonne grade est bien numérique
    df["grade"] = pd.to_numeric(df["grade"], errors="coerce")
    return df







