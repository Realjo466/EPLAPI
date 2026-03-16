import sys
from pathlib import Path

import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from visuals.boxplots import grade_boxplot_by


st.title("UE & matières")

notes = load_notes()

ue_codes = sorted(notes["ue_code"].dropna().unique())
ue_code = st.sidebar.selectbox("UE", ue_codes)

df_ue = notes[notes["ue_code"] == ue_code]

st.subheader("Statistiques par matière dans l'UE sélectionnée")
st.markdown(
    """
    Statistiques détaillées pour chaque matière de l'UE sélectionnée.
    """
)
stats = compute_descriptive_stats(df_ue, group_by=["subject_name"])
st.dataframe(stats, use_container_width=True)

st.subheader("Distribution des notes par matière (boxplot)")
st.markdown(
    """
    Le boxplot (diagramme en boîte) montre :
    - **Boîte** : 50% des notes (quartiles Q1 à Q3)
    - **Ligne centrale** : Médiane
    - **Moustaches** : Étendue des notes (hors valeurs aberrantes)
    - **Points** : Valeurs individuelles (notes extrêmes)
    
    Les statistiques détaillées par matière sont affichées dans l'encadré en haut à gauche.
    """
)
fig = grade_boxplot_by(
    df_ue,
    group_col="subject_name",
    title="Distribution des notes par matière",
    pass_threshold=10.0,
)
st.plotly_chart(fig, use_container_width=True)




