import sys
from pathlib import Path

import streamlit as st

# Assure que le dossier racine du projet est dans sys.path pour pouvoir importer `analysis` et `visuals`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.descriptive_stats import compute_descriptive_stats
from analysis.pass_rate import compute_pass_rate
from visuals.histograms import grade_histogram, grade_histogram_by_group


st.title("Vue globale")

notes = load_notes()

st.subheader("Indicateurs globaux")
global_stats = compute_descriptive_stats(notes, group_by=None)
row = global_stats.iloc[0]
pass_stats = compute_pass_rate(notes, group_by=None)
pass_rate = float(pass_stats["Taux de réussite (%)"].iloc[0])

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Nombre de notes", int(row["Effectif"]))
col2.metric("Moyenne", f"{row['Moyenne']:.2f}")
col3.metric("Médiane", f"{row['Médiane']:.2f}")
col4.metric("Écart-type", f"{row['Écart-type']:.2f}" if row["Écart-type"] is not None else "–")
col5.metric("Taux de réussite (≥10)", f"{pass_rate:.1f} %")

st.markdown(
    """
    ### Explication des indicateurs
    
    Ces indicateurs résument l'ensemble des notes de l'EPL :
    - **Nombre de notes** : Total des évaluations enregistrées
    - **Moyenne** : Note moyenne de tous les étudiants (indicateur de niveau général)
    - **Médiane** : Note qui sépare la moitié supérieure de la moitié inférieure (moins sensible aux valeurs extrêmes)
    - **Écart-type** : Mesure de la dispersion des notes (plus l'écart-type est élevé, plus les notes sont dispersées)
    - **Taux de réussite** : Pourcentage d'étudiants ayant obtenu une note ≥ 10/20 (seuil de réussite)
    """
)

st.subheader("Distribution globale des notes")
st.markdown(
    """
    L'histogramme ci-dessous montre la répartition de toutes les notes. 
    Les zones colorées indiquent les zones de réussite (vert) et d'échec (rouge).
    Les lignes verticales marquent la moyenne, la médiane et le seuil de réussite.
    """
)
fig = grade_histogram(notes, title="Distribution globale des notes (avec moyenne, médiane et seuil de réussite)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Comparaison des distributions par département")
st.markdown(
    """
    Ce graphique superpose les distributions de notes de chaque département pour faciliter la comparaison.
    Les statistiques détaillées par département sont affichées dans l'encadré en haut à gauche.
    """
)
fig_dep = grade_histogram_by_group(
    notes,
    group_col="department",
    title="Distribution des notes par département (superposition)",
    pass_threshold=10.0,
)
st.plotly_chart(fig_dep, use_container_width=True)




