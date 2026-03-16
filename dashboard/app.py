"""
Point d'entrée du tableau de bord Streamlit.

Lancer avec :
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Ajout du dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from dashboard.api_client import check_api_connection, get_api_url, set_api_url


st.set_page_config(
    page_title="EPL - Tableau de bord des notes",
    layout="wide",
)

st.title("Tableau de bord des notes de l'EPL")

# Configuration de l'API dans la sidebar
with st.sidebar:
    st.header("Configuration API")
    api_url = st.text_input(
        "URL de l'API FastAPI",
        value=get_api_url(),
        help="URL de base de l'API FastAPI (ex: http://localhost:8000)"
    )
    set_api_url(api_url)
    
    # Vérification de la connexion API
    if st.button("Vérifier la connexion"):
        if check_api_connection():
            st.success("API connectée")
        else:
            st.error("API non accessible. Assurez-vous que FastAPI est lancé.")
    
    # Indicateur de statut API
    api_status = check_api_connection()
    if api_status:
        st.success("API en ligne")
    else:
        st.warning("API hors ligne - Les données seront chargées depuis les CSV locaux")

st.markdown(
    """
Bienvenue sur le tableau de bord d'analyse des notes de l'EPL.

**Utilisation de l'API FastAPI :**
- Ce dashboard communique avec l'API FastAPI pour récupérer les statistiques.
- Configurez l'URL de l'API dans le menu de gauche.
- Si l'API n'est pas accessible, les données seront chargées depuis les CSV locaux.

Utilise le menu de gauche pour naviguer entre :
- **Upload CSV** - Téléverser vos propres fichiers CSV pour analyse
- **Vue globale** - KPIs et distributions globales
- **Départements** - Comparaison par département
- **Programmes** - Analyse par programme
- **Niveaux** - Licence / Master
- **UE & matières** - Détails par UE et matière
- **Classement** - Classement des étudiants
- **Exports** - Exporter les résultats
"""
)




