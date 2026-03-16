import sys
from pathlib import Path

import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.loader import load_notes
from analysis.ranking import compute_ranking


st.title("Classement des étudiants")

notes = load_notes()

# Filtres dans la sidebar
st.sidebar.header("Filtres de classement")

# Type de classement
group_mode = st.sidebar.selectbox(
    "Type de classement",
    ["Global", "Par département", "Par programme", "Par niveau"],
)

if group_mode == "Global":
    group_by = None
    # Filtres supplémentaires pour le classement global
    st.sidebar.subheader("Filtres additionnels")
    
    departments = sorted(notes["department"].dropna().unique())
    selected_departments = st.sidebar.multiselect(
        "Filtrer par département",
        departments,
        default=[],
        help="Sélectionnez un ou plusieurs départements pour filtrer le classement"
    )
    
    programs = sorted(notes["program"].dropna().unique())
    selected_programs = st.sidebar.multiselect(
        "Filtrer par programme",
        programs,
        default=[],
        help="Sélectionnez un ou plusieurs programmes pour filtrer le classement"
    )
    
    levels = sorted(notes["level"].dropna().unique())
    selected_levels = st.sidebar.multiselect(
        "Filtrer par niveau",
        levels,
        default=[],
        help="Sélectionnez un ou plusieurs niveaux pour filtrer le classement"
    )
    
    # Appliquer les filtres
    filtered_notes = notes.copy()
    if selected_departments:
        filtered_notes = filtered_notes[filtered_notes["department"].isin(selected_departments)]
    if selected_programs:
        filtered_notes = filtered_notes[filtered_notes["program"].isin(selected_programs)]
    if selected_levels:
        filtered_notes = filtered_notes[filtered_notes["level"].isin(selected_levels)]
    
    if len(filtered_notes) == 0:
        st.warning("Aucun étudiant ne correspond aux filtres sélectionnés.")
        st.stop()
    
    ranking_df = compute_ranking(filtered_notes, group_by=group_by)
    
elif group_mode == "Par département":
    group_by = ["department"]
    departments = sorted(notes["department"].dropna().unique())
    selected_department = st.sidebar.selectbox(
        "Sélectionner un département",
        departments,
        help="Choisissez le département pour lequel afficher le classement"
    )
    filtered_notes = notes[notes["department"] == selected_department]
    ranking_df = compute_ranking(filtered_notes, group_by=group_by)
    
elif group_mode == "Par programme":
    group_by = ["program"]
    programs = sorted(notes["program"].dropna().unique())
    selected_program = st.sidebar.selectbox(
        "Sélectionner un programme",
        programs,
        help="Choisissez le programme pour lequel afficher le classement"
    )
    filtered_notes = notes[notes["program"] == selected_program]
    ranking_df = compute_ranking(filtered_notes, group_by=group_by)
    
else:  # Par niveau
    group_by = ["level"]
    levels = sorted(notes["level"].dropna().unique())
    selected_level = st.sidebar.selectbox(
        "Sélectionner un niveau",
        levels,
        help="Choisissez le niveau pour lequel afficher le classement"
    )
    filtered_notes = notes[notes["level"] == selected_level]
    ranking_df = compute_ranking(filtered_notes, group_by=group_by)

# Filtres de plage de moyenne
st.sidebar.subheader("Filtres de moyenne")
min_average = st.sidebar.slider(
    "Moyenne minimum",
    min_value=0.0,
    max_value=20.0,
    value=0.0,
    step=0.5,
    help="Filtrer les étudiants avec une moyenne supérieure ou égale à cette valeur"
)
max_average = st.sidebar.slider(
    "Moyenne maximum",
    min_value=0.0,
    max_value=20.0,
    value=20.0,
    step=0.5,
    help="Filtrer les étudiants avec une moyenne inférieure ou égale à cette valeur"
)

# Appliquer le filtre de moyenne
if "Moyenne" in ranking_df.columns:
    ranking_df = ranking_df[
        (ranking_df["Moyenne"] >= min_average) & 
        (ranking_df["Moyenne"] <= max_average)
    ]

# Recherche par identifiant étudiant
st.sidebar.subheader("Recherche")
search_id = st.sidebar.text_input(
    "Rechercher un étudiant (ID)",
    help="Entrez l'identifiant d'un étudiant pour le trouver dans le classement"
)

# Nombre d'étudiants à afficher
top_n = st.sidebar.slider(
    "Nombre d'étudiants à afficher",
    min_value=10,
    max_value=min(500, len(ranking_df)),
    value=min(50, len(ranking_df)),
    step=10
)

# Affichage des résultats
if search_id:
    # Rechercher l'étudiant
    if "Identifiant étudiant" in ranking_df.columns:
        student_results = ranking_df[
            ranking_df["Identifiant étudiant"].str.contains(search_id, case=False, na=False)
        ]
        if len(student_results) > 0:
            st.subheader(f"Résultats de recherche pour : {search_id}")
            st.dataframe(student_results, use_container_width=True)
        else:
            st.info(f"Aucun étudiant trouvé avec l'identifiant contenant '{search_id}'")
    else:
        st.warning("La colonne 'Identifiant étudiant' n'est pas disponible dans les résultats.")
else:
    # Afficher le classement
    if group_mode == "Global" and (selected_departments or selected_programs or selected_levels):
        st.subheader(f"Top {top_n} - {group_mode} (avec filtres)")
    else:
        st.subheader(f"Top {top_n} - {group_mode}")
    
    st.markdown(
        """
        Le classement est basé sur la moyenne pondérée par les crédits de chaque UE.
        Les étudiants sont triés par moyenne décroissante.
        """
    )
    
    # Statistiques du classement
    if len(ranking_df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre total d'étudiants", len(ranking_df))
        with col2:
            if "Moyenne" in ranking_df.columns:
                st.metric("Moyenne maximale", f"{ranking_df['Moyenne'].max():.2f}")
        with col3:
            if "Moyenne" in ranking_df.columns:
                st.metric("Moyenne minimale", f"{ranking_df['Moyenne'].min():.2f}")
        with col4:
            if "Moyenne" in ranking_df.columns:
                st.metric("Moyenne globale", f"{ranking_df['Moyenne'].mean():.2f}")
    
    st.dataframe(ranking_df.head(top_n), use_container_width=True)
    
    # Option de téléchargement
    if len(ranking_df) > 0:
        csv_data = ranking_df.to_csv(index=False)
        st.download_button(
            label="Télécharger le classement complet (CSV)",
            data=csv_data,
            file_name=f"classement_{group_mode.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )




