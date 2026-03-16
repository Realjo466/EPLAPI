"""
Calcul du taux de réussite (réussite = grade >= seuil).
"""

from typing import Iterable

import pandas as pd


def compute_pass_rate(df: pd.DataFrame, group_by: Iterable[str] | None, threshold: float = 10.0) -> pd.DataFrame:
    """
    Calcule le taux de réussite par groupes.

    Parameters
    ----------
    df : DataFrame avec une colonne `grade`
    group_by : liste de colonnes pour le groupement (None pour global)
    threshold : note minimale pour considérer une réussite
    """
    df = df.copy()
    df["is_pass"] = df["grade"] >= threshold

    # Gestion du cas "global" (aucun groupement)
    if not group_by:
        pass_count = int(df["is_pass"].sum())
        total = int(df["is_pass"].count())
        pass_rate = round((pass_count / total * 100), 2) if total > 0 else 0.0
        
        result = pd.DataFrame({
            "Réussis": [pass_count],
            "Total": [total],
            "Taux de réussite (%)": [pass_rate]
        })
    else:
        if isinstance(group_by, str):
            group_by = [group_by]
        group_by = list(group_by)  # type: ignore

        grouped = df.groupby(group_by)

        result = grouped["is_pass"].agg(
            Réussis="sum",
            Total="count",
        ).reset_index()
        result["Taux de réussite (%)"] = (result["Réussis"] / result["Total"] * 100).round(2)

    return result







