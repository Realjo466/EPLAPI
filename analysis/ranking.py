"""
Classement des étudiants sur base de la moyenne pondérée par crédits.
"""

from typing import Iterable, List

import pandas as pd


def compute_ranking(
    df: pd.DataFrame,
    group_by: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Calcule la moyenne pondérée par crédits pour chaque étudiant et,
    éventuellement, par groupe (département, programme, niveau).

    Parameters
    ----------
    df : DataFrame
        Doit contenir `student_id`, `grade`, `credit` et les éventuelles colonnes de groupement.
    group_by : liste de colonnes pour calculer un classement par groupe.
               Exemple : ["department", "program", "level"]
               Si None -> classement global.
    """
    if group_by is None:
        group_by_cols: List[str] = []
    elif isinstance(group_by, str):
        group_by_cols = [group_by]  # type: ignore
    else:
        group_by_cols = list(group_by)  # type: ignore

    # Colonnes de groupement complètes : (groupes éventuels) + student_id
    full_group = group_by_cols + ["student_id"]

    # Moyenne pondérée par crédits
    agg = (
        df.groupby(full_group)
        .apply(lambda g: (g["grade"] * g["credit"]).sum() / g["credit"].sum())
        .reset_index(name="avg_grade")
    )

    # Classement par groupe
    if group_by_cols:
        agg["Rang"] = (
            agg.groupby(group_by_cols)["avg_grade"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )
    else:
        agg["Rang"] = agg["avg_grade"].rank(method="dense", ascending=False).astype(int)

    agg["Moyenne"] = agg["avg_grade"].round(2)
    agg = agg.drop(columns=["avg_grade"])
    
    # Renommer student_id
    if "student_id" in agg.columns:
        agg = agg.rename(columns={"student_id": "Identifiant étudiant"})

    return agg.sort_values(group_by_cols + ["Rang"] if group_by_cols else ["Rang"])







