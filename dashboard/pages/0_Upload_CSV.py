"""
Page Streamlit pour uploader des fichiers CSV pour analyse.

Cette page permet de téléverser des fichiers CSV qui seront traités par l'API FastAPI.
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from dashboard.api_client import upload_csv, check_api_connection, get_api_url


st.title("Upload de fichiers CSV")

st.markdown(
    """
    ### Instructions
    
    Téléversez un fichier CSV contenant les notes des étudiants avec les colonnes suivantes :
    
    - `student_id` : Identifiant de l'étudiant
    - `department` : Département
    - `program` : Programme
    - `level` : Niveau (ex: "License Genie civile")
    - `ue_code` : Code de l'UE
    - `ue_name` : Nom de l'UE
    - `subject_code` : Code de la matière
    - `subject_name` : Nom de la matière
    - `teacher` : Enseignant
    - `credit` : Nombre de crédits
    - `grade` : Note (valeur numérique)
    
    **Format attendu :** CSV avec séparateur virgule (`,`)
    """
)

# Vérification de la connexion API
if not check_api_connection():
    st.error(
        f"""
        **API FastAPI non accessible**
        
        L'API doit être lancée pour pouvoir uploader des fichiers.
        
        Pour lancer l'API :
        ```bash
        uvicorn main:app --reload
        ```
        
        URL actuelle : `{get_api_url()}`
        """
    )
    st.stop()

st.info(f"**API connectée** : `{get_api_url()}`")

# Zone d'upload
uploaded_file = st.file_uploader(
    "Choisir un fichier CSV",
    type=["csv"],
    help="Sélectionnez un fichier CSV avec les colonnes requises"
)

if uploaded_file is not None:
    st.subheader("Aperçu du fichier")
    
    try:
        # Afficher un aperçu du CSV
        df_preview = pd.read_csv(uploaded_file)
        st.dataframe(df_preview.head(10))
        st.caption(f"Nombre total de lignes : {len(df_preview)}")
        
        # Vérifier les colonnes requises
        required_columns = [
            "student_id", "department", "program", "level", "ue_code",
            "ue_name", "subject_code", "subject_name", "teacher", "credit", "grade"
        ]
        missing_columns = [col for col in required_columns if col not in df_preview.columns]
        
        if missing_columns:
            st.error(f"**Colonnes manquantes** : {', '.join(missing_columns)}")
        else:
            st.success("**Toutes les colonnes requises sont présentes**")
            
            # Bouton d'upload
            if st.button("Uploader le fichier vers l'API", type="primary"):
                with st.spinner("Upload en cours..."):
                    try:
                        # Réinitialiser le pointeur du fichier
                        uploaded_file.seek(0)
                        file_content = uploaded_file.read()
                        
                        # Upload via l'API
                        result = upload_csv(file_content, uploaded_file.name)
                        
                        st.success(f"**Fichier uploadé avec succès !**")
                        st.json(result)
                        
                        st.info(
                            """
                            **Prochaines étapes :**
                            - Le fichier a été sauvegardé sur le serveur
                            - Vous pouvez maintenant utiliser les autres pages du dashboard pour analyser les données
                            - Les statistiques seront calculées à partir du fichier uploadé
                            """
                        )
                    except Exception as e:
                        st.error(f"**Erreur lors de l'upload** : {str(e)}")
    
    except pd.errors.EmptyDataError:
        st.error("Le fichier CSV est vide")
    except pd.errors.ParserError as e:
        st.error(f"Erreur de parsing CSV : {str(e)}")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")

# Section d'exemple
with st.expander("Exemple de format CSV"):
    st.markdown(
        """
        Voici un exemple de ligne CSV :
        ```
        student_id,department,program,level,ue_code,ue_name,subject_code,subject_name,teacher,credit,grade
        STU001,Informatique,Génie Logiciel,License Informatique et Systeme,UE-INF-101,Algorithmique,SUB-INF-101,Algo 1,Dr A,6,14
        ```
        """
    )
    
    # Générer un exemple de DataFrame
    example_data = {
        "student_id": ["STU001", "STU002"],
        "department": ["Informatique", "Informatique"],
        "program": ["Génie Logiciel", "Génie Logiciel"],
        "level": ["License Informatique et Systeme", "License Informatique et Systeme"],
        "ue_code": ["UE-INF-101", "UE-INF-101"],
        "ue_name": ["Algorithmique", "Algorithmique"],
        "subject_code": ["SUB-INF-101", "SUB-INF-101"],
        "subject_name": ["Algo 1", "Algo 1"],
        "teacher": ["Dr A", "Dr A"],
        "credit": [6, 6],
        "grade": [14, 12]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df)




