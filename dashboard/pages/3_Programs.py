import sys
from pathlib import Path

import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from visuals.barcharts import mean_bar_by


st.title("Programmes")

notes = load_notes()
programs = sorted(notes["program"].dropna().unique())

program = st.sidebar.selectbox("Programme", programs)

df_prog = notes[notes["program"] == program]

st.subheader(f"Statistiques par UE - {program}")

stats = compute_descriptive_stats(df_prog, group_by=["ue_code", "ue_name"])
st.dataframe(stats, use_container_width=True)

st.subheader("Moyenne des notes par UE")
st.markdown(
    """
    Graphique comparant les moyennes des notes par Unité d'Enseignement (UE).
    Les barres d'erreur représentent l'écart-type.
    """
)
fig = mean_bar_by(
    df_prog, 
    group_col="ue_name", 
    title=f"Moyenne par UE - {program}",
    pass_threshold=10.0,
)
st.plotly_chart(fig, use_container_width=True)




