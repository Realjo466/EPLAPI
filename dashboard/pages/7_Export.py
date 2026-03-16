import sys
from pathlib import Path

import numpy as np
import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import ROOT, load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from analysis.ranking import compute_ranking


st.title("Exports")

notes = load_notes()

EXPORT_DIR = ROOT / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

stats_csv_path = EXPORT_DIR / "stats_export.csv"
ranking_npy_path = EXPORT_DIR / "ranking_export.npy"

st.markdown(
    """
    ### Exporter les données
    
    Utilisez les boutons ci-dessous pour exporter les statistiques et classements au format CSV ou NumPy.
    Les fichiers seront sauvegardés dans le dossier `data/exports/`.
    """
)

if st.button("Exporter les statistiques globales en CSV", type="primary"):
    stats = compute_descriptive_stats(notes, group_by=["department", "program", "level"])
    stats.to_csv(stats_csv_path, index=False)
    st.success(f"Statistiques exportées avec succès dans : `{stats_csv_path}`")
    st.download_button(
        label="Télécharger le fichier CSV",
        data=stats.to_csv(index=False),
        file_name="stats_export.csv",
        mime="text/csv",
    )

if st.button("Exporter le classement global en NumPy (.npy)", type="primary"):
    ranking_df = compute_ranking(notes, group_by=None)
    np.save(ranking_npy_path, ranking_df.to_records(index=False))
    st.success(f"Classement exporté avec succès dans : `{ranking_npy_path}`")
    st.info("Pour charger le fichier NumPy : `np.load('ranking_export.npy')`")




