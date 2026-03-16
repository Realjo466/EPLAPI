"""
Client API pour communiquer avec le backend FastAPI.

Ce module centralise tous les appels à l'API FastAPI depuis Streamlit.
Toutes les pages du dashboard utilisent ce client au lieu de charger directement les CSV.
"""

import requests
from typing import Dict, List, Optional
import streamlit as st


# URL de base de l'API FastAPI (configurable via session state)
API_BASE_URL = "http://localhost:8000"


def get_api_url() -> str:
    """
    Récupère l'URL de l'API depuis la session state ou utilise la valeur par défaut.
    
    Returns:
        str: URL de base de l'API
    """
    return st.session_state.get("api_url", API_BASE_URL)


def set_api_url(url: str):
    """
    Définit l'URL de l'API dans la session state.
    
    Args:
        url: URL de base de l'API (ex: "http://localhost:8000")
    """
    st.session_state["api_url"] = url


def check_api_connection() -> bool:
    """
    Vérifie si l'API FastAPI est accessible.
    
    Returns:
        bool: True si l'API est accessible, False sinon
    """
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_global_stats() -> Dict:
    """
    Récupère les statistiques globales via l'API.
    
    Returns:
        Dict: Dictionnaire contenant 'stats' et 'pass_rate'
    
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/stats/global")
    response.raise_for_status()
    return response.json()


def get_department_stats(department: str) -> Dict:
    """
    Récupère les statistiques par matière pour un département via l'API.
    
    Args:
        department: Nom du département
        
    Returns:
        Dict: Dictionnaire contenant 'stats' et 'pass_rate' par matière
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/stats/department/{department}")
    response.raise_for_status()
    return response.json()


def get_program_stats(program: str) -> Dict:
    """
    Récupère les statistiques par UE pour un programme via l'API.
    
    Args:
        program: Nom du programme
        
    Returns:
        Dict: Dictionnaire contenant 'stats' et 'pass_rate' par UE
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/stats/program/{program}")
    response.raise_for_status()
    return response.json()


def get_level_stats(level: str) -> Dict:
    """
    Récupère les statistiques par département pour un niveau via l'API.
    
    Args:
        level: Niveau (ex: "License Genie civile", "Master Informatique et Systeme")
        
    Returns:
        Dict: Dictionnaire contenant 'stats' et 'pass_rate' par département
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/stats/level/{level}")
    response.raise_for_status()
    return response.json()


def get_ue_stats(ue_code: str) -> Dict:
    """
    Récupère les statistiques par matière pour une UE via l'API.
    
    Args:
        ue_code: Code de l'UE
        
    Returns:
        Dict: Dictionnaire contenant 'stats' et 'pass_rate' par matière
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/stats/ue/{ue_code}")
    response.raise_for_status()
    return response.json()


def get_global_ranking(group_by: Optional[List[str]] = None) -> List[Dict]:
    """
    Récupère le classement global via l'API.
    
    Args:
        group_by: Liste des colonnes pour grouper (None pour global)
        
    Returns:
        List[Dict]: Liste des étudiants classés
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    params = {}
    if group_by:
        params["group_by"] = ",".join(group_by)
    response = requests.get(f"{get_api_url()}/ranking/global", params=params)
    response.raise_for_status()
    return response.json()


def get_departments() -> List[str]:
    """
    Récupère la liste des départements via l'API.
    
    Returns:
        List[str]: Liste des départements
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/departments")
    response.raise_for_status()
    return response.json()


def get_programs() -> List[str]:
    """
    Récupère la liste des programmes via l'API.
    
    Returns:
        List[str]: Liste des programmes
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/programs")
    response.raise_for_status()
    return response.json()


def get_levels() -> List[str]:
    """
    Récupère la liste des niveaux via l'API.
    
    Returns:
        List[str]: Liste des niveaux
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    response = requests.get(f"{get_api_url()}/levels")
    response.raise_for_status()
    return response.json()


def upload_csv(file_content: bytes, filename: str) -> Dict:
    """
    Upload un fichier CSV vers l'API pour analyse.
    
    Args:
        file_content: Contenu du fichier en bytes
        filename: Nom du fichier
        
    Returns:
        Dict: Réponse de l'API avec le statut de l'upload
        
    Raises:
        requests.RequestException: Si l'appel API échoue
    """
    files = {"file": (filename, file_content, "text/csv")}
    response = requests.post(f"{get_api_url()}/upload", files=files)
    response.raise_for_status()
    return response.json()




