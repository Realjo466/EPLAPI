import sys
from pathlib import Path

import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from analysis.pass_rate import compute_pass_rate
from visuals.barcharts import mean_bar_by, pass_rate_bar_by


st.title("Niveaux (Licence / Master)")

notes = load_notes()
levels = sorted(notes["level"].dropna().unique())

level = st.sidebar.selectbox("Niveau", levels)

df_level = notes[notes["level"] == level]

st.subheader(f"Statistiques globales - {level}")

stats = compute_descriptive_stats(df_level, group_by=None)
st.dataframe(stats, use_container_width=True)

pass_stats = compute_pass_rate(df_level, group_by=None)
col1, col2 = st.columns(2)
with col1:
    st.metric("Taux de réussite global (≥10)", f"{pass_stats['Taux de réussite (%)'].iloc[0]:.1f} %")
with col2:
    st.metric("Nombre total d'étudiants", int(pass_stats['Total'].iloc[0]))

st.subheader("Moyenne des notes par département")
st.markdown(
    """
    Les barres d'erreur représentent l'écart-type. Les barres sont colorées selon la performance :
    - Vert : moyenne ≥ 10/20 (au-dessus du seuil de réussite)
    - Rouge : moyenne < 10/20 (en dessous du seuil)
    """
)
fig = mean_bar_by(
    df_level,
    group_col="department",
    title=f"Moyenne des notes par département - {level}",
    pass_threshold=10.0,
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Taux de réussite par département")
st.markdown(
    """
    Le taux de réussite indique le pourcentage d'étudiants ayant obtenu ≥ 10/20.
    Les lignes de référence montrent la moyenne globale et les seuils d'objectif (50%) et d'alerte (30%).
    """
)
fig_pass = pass_rate_bar_by(
    df_level,
    group_col="department",
    title=f"Taux de réussite (≥10) par département - {level}",
    threshold=10.0,
)
st.plotly_chart(fig_pass, use_container_width=True)




