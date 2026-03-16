"""
Backend FastAPI pour exposer les statistiques des notes EPL.

Endpoints principaux :
- GET /health - Vérification de l'état de l'API
- GET /stats/global - Statistiques globales
- GET /stats/department/{department} - Stats par département
- GET /stats/program/{program} - Stats par programme
- GET /stats/level/{level} - Stats par niveau
- GET /stats/ue/{ue_code} - Stats par UE
- GET /ranking/global - Classement des étudiants
- GET /departments - Liste des départements
- GET /programs - Liste des programmes
- GET /levels - Liste des niveaux
- POST /upload - Upload de CSV pour analyse
"""

import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File

from analysis.loader import load_notes, ROOT
from analysis.descriptive_stats import compute_descriptive_stats
from analysis.pass_rate import compute_pass_rate
from analysis.ranking import compute_ranking


app = FastAPI(title="EPL Grades API", version="1.0.0")

# Dossier pour les CSV uploadés
UPLOAD_DIR = ROOT / "data" / "uploaded"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/stats/global")
def get_global_stats():
    """
    Statistiques globales (toutes notes confondues).
    """
    notes = load_notes()
    stats = compute_descriptive_stats(notes, group_by=[]).to_dict(orient="records")
    pass_rate = compute_pass_rate(notes, group_by=[]).to_dict(orient="records")
    return {"stats": stats, "pass_rate": pass_rate}


@app.get("/stats/department/{department}")
def get_department_stats(department: str):
    """
    Statistiques par matière pour un département donné.
    """
    notes = load_notes()
    df = notes[notes["department"] == department]
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée pour ce département.")

    stats = compute_descriptive_stats(df, group_by=["subject_code", "subject_name"]).to_dict(
        orient="records"
    )
    pass_rate = compute_pass_rate(
        df, group_by=["subject_code", "subject_name"]
    ).to_dict(orient="records")

    return {"department": department, "stats": stats, "pass_rate": pass_rate}


@app.get("/health")
def health_check():
    """
    Vérification de l'état de l'API.
    """
    return {"status": "ok", "message": "API EPL Grades est opérationnelle"}


@app.get("/ranking/global")
def get_global_ranking(top_n: int = 50, group_by: Optional[str] = None):
    """
    Classement global des étudiants (moyenne pondérée par crédits).
    
    Args:
        top_n: Nombre d'étudiants à retourner (défaut: 50)
        group_by: Colonnes pour grouper, séparées par des virgules (ex: "department,program")
    """
    notes = load_notes()
    group_by_list = None
    if group_by:
        group_by_list = [col.strip() for col in group_by.split(",")]
    ranking_df = compute_ranking(notes, group_by=group_by_list)
    ranking_top = ranking_df.sort_values("rank").head(top_n)
    return {"top_n": top_n, "ranking": ranking_top.to_dict(orient="records")}


@app.get("/departments")
def list_departments() -> List[str]:
    """
    Renvoie la liste des départements disponibles dans les données.
    """
    notes = load_notes()
    return sorted(notes["department"].dropna().unique().tolist())


@app.get("/programs")
def list_programs() -> List[str]:
    """
    Renvoie la liste des programmes disponibles dans les données.
    """
    notes = load_notes()
    return sorted(notes["program"].dropna().unique().tolist())


@app.get("/levels")
def list_levels() -> List[str]:
    """
    Renvoie la liste des niveaux disponibles dans les données.
    """
    notes = load_notes()
    return sorted(notes["level"].dropna().unique().tolist())


@app.get("/stats/program/{program}")
def get_program_stats(program: str):
    """
    Statistiques par UE pour un programme donné.
    """
    notes = load_notes()
    df = notes[notes["program"] == program]
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour le programme '{program}'.")

    stats = compute_descriptive_stats(df, group_by=["ue_code", "ue_name"]).to_dict(orient="records")
    pass_rate = compute_pass_rate(df, group_by=["ue_code", "ue_name"]).to_dict(orient="records")

    return {"program": program, "stats": stats, "pass_rate": pass_rate}


@app.get("/stats/level/{level}")
def get_level_stats(level: str):
    """
    Statistiques par département pour un niveau donné.
    """
    notes = load_notes()
    df = notes[notes["level"] == level]
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour le niveau '{level}'.")

    stats = compute_descriptive_stats(df, group_by=["department"]).to_dict(orient="records")
    pass_rate = compute_pass_rate(df, group_by=["department"]).to_dict(orient="records")

    return {"level": level, "stats": stats, "pass_rate": pass_rate}


@app.get("/stats/ue/{ue_code}")
def get_ue_stats(ue_code: str):
    """
    Statistiques par matière pour une UE donnée.
    """
    notes = load_notes()
    df = notes[notes["ue_code"] == ue_code]
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour l'UE '{ue_code}'.")

    stats = compute_descriptive_stats(df, group_by=["subject_code", "subject_name"]).to_dict(orient="records")
    pass_rate = compute_pass_rate(df, group_by=["subject_code", "subject_name"]).to_dict(orient="records")

    return {"ue_code": ue_code, "stats": stats, "pass_rate": pass_rate}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload un fichier CSV pour analyse.
    
    Le fichier doit avoir les colonnes : student_id, department, program, level, 
    ue_code, ue_name, subject_code, subject_name, teacher, credit, grade
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV (.csv)")
    
    try:
        # Lire le contenu du fichier
        contents = await file.read()
        
        # Sauvegarder le fichier
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Valider le format CSV
        df = pd.read_csv(file_path)
        required_columns = [
            "student_id", "department", "program", "level", "ue_code", 
            "ue_name", "subject_code", "subject_name", "teacher", "credit", "grade"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Colonnes manquantes dans le CSV : {', '.join(missing_columns)}"
            )
        
        # Vérifier que 'grade' est numérique
        if not pd.api.types.is_numeric_dtype(df["grade"]):
            raise HTTPException(
                status_code=400,
                detail="La colonne 'grade' doit contenir des valeurs numériques"
            )
        
        # Remplacer le fichier notes_epl.csv par défaut (optionnel, on peut aussi créer un nouveau fichier)
        # Ici, on sauvegarde dans uploaded/ et on peut l'utiliser plus tard
        return {
            "status": "success",
            "message": f"Fichier '{file.filename}' uploadé avec succès",
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "file_path": str(file_path)
        }
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Le fichier CSV est vide")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Erreur de parsing CSV : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload : {str(e)}")




