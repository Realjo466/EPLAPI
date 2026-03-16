"""
Fonctions de filtrage génériques pour les DataFrames de notes.
"""

import pandas as pd


def filter_by_department(df: pd.DataFrame, department: str) -> pd.DataFrame:
    return df[df["department"] == department]


def filter_by_program(df: pd.DataFrame, program: str) -> pd.DataFrame:
    return df[df["program"] == program]


def filter_by_level(df: pd.DataFrame, level: str) -> pd.DataFrame:
    return df[df["level"] == level]


def filter_by_ue(df: pd.DataFrame, ue_code: str) -> pd.DataFrame:
    return df[df["ue_code"] == ue_code]


def filter_by_subject(df: pd.DataFrame, subject_code: str) -> pd.DataFrame:
    return df[df["subject_code"] == subject_code]







