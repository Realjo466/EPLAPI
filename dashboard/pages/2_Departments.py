import sys
from pathlib import Path

import streamlit as st

# Ajouter le dossier racine du projet au PYTHONPATH pour accéder à `analysis` et `visuals`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from analysis.pass_rate import compute_pass_rate
from visuals.barcharts import mean_bar_by, pass_rate_bar_by


st.title("Départements")

notes = load_notes()
departments = sorted(notes["department"].dropna().unique())

department = st.sidebar.selectbox("Département", departments)

df_dep = notes[notes["department"] == department]

st.subheader(f"Statistiques par matière - {department}")

stats = compute_descriptive_stats(df_dep, group_by=["subject_name"])
pass_stats = compute_pass_rate(df_dep, group_by=["subject_name"])

st.markdown(
    """
    ### Explication du tableau
    
    Le tableau ci-dessous présente pour chaque matière :
    - **Effectif** : Nombre total de notes enregistrées
    - **Moyenne** : Moyenne des notes
    - **Médiane** : Médiane des notes
    - **Écart-type** : Écart-type (mesure de dispersion)
    - **Minimum** : Note minimale observée
    - **Maximum** : Note maximale observée
    """
)
st.dataframe(stats, use_container_width=True)

st.subheader("Moyenne et variabilité par matière")
st.markdown(
    """
    Les barres d'erreur représentent l'écart-type. Les barres sont colorées selon la performance :
    - Vert : moyenne ≥ 10/20
    - Rouge : moyenne < 10/20
    """
)
fig_mean = mean_bar_by(
    df_dep,
    group_col="subject_name",
    title=f"Moyenne des notes (barres d'erreur = écart-type) - {department}",
    pass_threshold=10.0,
)
st.plotly_chart(fig_mean, use_container_width=True)

st.subheader("Taux de réussite par matière")
st.markdown(
    """
    Le taux de réussite indique le pourcentage d'étudiants ayant obtenu ≥ 10/20 dans chaque matière.
    Les valeurs affichées sur les barres montrent le taux et le nombre d'étudiants (réussis/total).
    """
)
fig_pass = pass_rate_bar_by(
    df_dep,
    group_col="subject_name",
    title=f"Taux de réussite (≥10) par matière - {department}",
    threshold=10.0,
)
st.plotly_chart(fig_pass, use_container_width=True)




