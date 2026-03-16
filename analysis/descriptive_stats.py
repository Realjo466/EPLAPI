"""
Statistiques descriptives sur les notes :
- moyenne
- médiane
- écart-type
- min, max
- effectif
"""

from typing import Iterable, List

import numpy as np
import pandas as pd


def compute_descriptive_stats(df: pd.DataFrame, group_by: Iterable[str] | None) -> pd.DataFrame:
    """
    Calcule des statistiques descriptives de la colonne `grade`
    par groupes.

    Parameters
    ----------
    df : DataFrame
        Doit contenir une colonne `grade`.
    group_by : liste de colonnes

    Returns
    -------
    DataFrame avec colonnes :
        - group_by...
        - count
        - mean
        - median
        - std
        - min
        - max
    """
    # Gestion du cas "global" (aucun groupement)
    if not group_by:
        series = df["grade"]
        stats = pd.DataFrame(
            {
                "count": [int(series.count())],
                "mean": [float(series.mean())],
                "median": [float(series.median())],
                "std": [float(series.std()) if not series.empty else np.nan],
                "min": [float(series.min()) if not series.empty else np.nan],
                "max": [float(series.max()) if not series.empty else np.nan],
            }
        )
    else:
        if isinstance(group_by, str):
            group_by = [group_by]
        group_by = list(group_by)  # type: ignore

        grouped = df.groupby(group_by)["grade"]

        stats = grouped.agg(
            count="count",
            mean="mean",
            std="std",
            min="min",
            max="max",
        ).reset_index()

        # Médiane séparément (agg ne l'ajoute pas toujours proprement selon version)
        median = grouped.median().reset_index(name="median")
        stats = stats.merge(median, on=group_by, how="left")

    # Arrondir pour une présentation plus propre
    numeric_cols: List[str] = ["mean", "median", "std", "min", "max"]
    for col in numeric_cols:
        if col in stats.columns:
            stats[col] = stats[col].astype(float).replace({np.nan: None})
            stats[col] = stats[col].round(2)

    # Renommer les colonnes en français pour l'affichage
    column_mapping = {
        "count": "Effectif",
        "mean": "Moyenne",
        "median": "Médiane",
        "std": "Écart-type",
        "min": "Minimum",
        "max": "Maximum",
    }
    stats = stats.rename(columns=column_mapping)

    return stats




