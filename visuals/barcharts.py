"""
Graphiques en barres explicatifs (moyenne, écart-type, taux de réussite) avec Plotly.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analysis.descriptive_stats import compute_descriptive_stats
from analysis.pass_rate import compute_pass_rate


def mean_bar_by(
    df: pd.DataFrame,
    group_col: str,
    title: str = "Moyenne des notes par groupe",
    pass_threshold: float = 10.0,
) -> go.Figure:
    """
    Graphique en barres de la moyenne des notes par groupe avec barres d'erreur.
    Inclut une ligne de référence pour le seuil de réussite et un code couleur.

    Parameters
    ----------
    df : DataFrame avec colonne `grade`
    group_col : colonne de groupement (ex. department, program, level, ue_name)
    pass_threshold : seuil de réussite (par défaut 10/20)
    """
    stats = compute_descriptive_stats(df, group_by=[group_col])
    
    # Trier par moyenne décroissante pour meilleure lisibilité
    stats = stats.sort_values("Moyenne", ascending=True)

    # Code couleur : vert si moyenne >= seuil, rouge sinon
    colors = ["#06A77D" if m >= pass_threshold else "#C73E1D" for m in stats["Moyenne"]]

    fig = px.bar(
        stats,
        x=group_col,
        y="Moyenne",
        error_y="Écart-type",
        title=title,
        labels={"Moyenne": "Moyenne (/20)", "Écart-type": "Écart-type", group_col: group_col},
        color=stats["Moyenne"],
        color_continuous_scale=["#C73E1D", "#F18F01", "#06A77D"],
    )
    
    # Ligne de référence pour le seuil de réussite
    fig.add_hline(
        y=pass_threshold,
        line_dash="solid",
        line_width=2.5,
        line_color="#C73E1D",
        annotation_text=f"Seuil de réussite = {pass_threshold}/20",
        annotation_position="right",
        annotation=dict(font_size=11, font_color="#C73E1D", bgcolor="rgba(240,240,240,0.9)", bordercolor="#C73E1D", borderwidth=1),
    )
    
    # Moyenne globale
    global_mean = df["grade"].mean()
    fig.add_hline(
        y=global_mean,
        line_dash="dash",
        line_width=2,
        line_color="black",
        annotation_text=f"Moyenne globale = {global_mean:.2f}/20",
        annotation_position="left",
        annotation=dict(font_size=10, bgcolor="rgba(240,240,240,0.9)", bordercolor="black", borderwidth=1),
    )
    
    # Ajouter les valeurs sur les barres
    fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
        hovertemplate=f"<b>{group_col}:</b> %{{x}}<br><b>Moyenne:</b> %{{y:.2f}}/20<br><b>Écart-type:</b> %{{customdata[0]:.2f}}<br><b>Effectif:</b> %{{customdata[1]}}<extra></extra>",
        customdata=stats[["Écart-type", "Effectif"]].values,
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title=group_col,
        yaxis_title="Moyenne (/20)",
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        yaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        showlegend=False,
        height=500,
    )
    
    return fig


def pass_rate_bar_by(
    df: pd.DataFrame,
    group_col: str,
    title: str = "Taux de réussite par groupe",
    threshold: float = 10.0,
) -> go.Figure:
    """
    Graphique en barres du taux de réussite (>= threshold) par groupe.
    Inclut des lignes de référence et un code couleur explicatif.

    Parameters
    ----------
    df : DataFrame avec colonne `grade`
    group_col : colonne de groupement (ex. department, program, level, ue_name)
    threshold : seuil de réussite
    """
    stats = compute_pass_rate(df, group_by=[group_col], threshold=threshold)
    
    # Trier par taux de réussite décroissant
    stats = stats.sort_values("Taux de réussite (%)", ascending=True)
    
    # Code couleur : vert si >= 50%, orange si >= 30%, rouge sinon
    colors = []
    for rate in stats["Taux de réussite (%)"]:
        if rate >= 50:
            colors.append("#06A77D")  # Vert
        elif rate >= 30:
            colors.append("#F18F01")  # Orange
        else:
            colors.append("#C73E1D")  # Rouge
    
    fig = px.bar(
        stats,
        x=group_col,
        y="Taux de réussite (%)",
        title=title,
        labels={"Taux de réussite (%)": "Taux de réussite (%)", group_col: group_col},
        text="Taux de réussite (%)",
        color=stats["Taux de réussite (%)"],
        color_continuous_scale=["#C73E1D", "#F18F01", "#06A77D"],
    )
    
    # Lignes de référence
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_width=2,
        line_color="#06A77D",
        annotation_text="50% (objectif)",
        annotation_position="right",
        annotation=dict(font_size=10, font_color="#06A77D", bgcolor="rgba(240,240,240,0.9)", bordercolor="#06A77D", borderwidth=1),
    )
    
    fig.add_hline(
        y=30,
        line_dash="dot",
        line_width=1.5,
        line_color="#F18F01",
        annotation_text="30% (seuil d'alerte)",
        annotation_position="right",
        annotation=dict(font_size=9, font_color="#F18F01", bgcolor="rgba(240,240,240,0.9)", bordercolor="#F18F01", borderwidth=1),
    )
    
    # Taux de réussite global
    global_pass_rate = (df["grade"] >= threshold).sum() / len(df) * 100
    fig.add_hline(
        y=global_pass_rate,
        line_dash="solid",
        line_width=2,
        line_color="black",
        annotation_text=f"Moyenne globale = {global_pass_rate:.1f}%",
        annotation_position="left",
        annotation=dict(font_size=10, bgcolor="rgba(240,240,240,0.9)", bordercolor="black", borderwidth=1),
    )
    
    # Ajouter les valeurs et effectifs sur les barres
    fig.update_traces(
        texttemplate="%{text:.1f}%<br>(%{customdata[0]}/%{customdata[1]})",
        textposition="outside",
        hovertemplate=f"<b>{group_col}:</b> %{{x}}<br><b>Taux de réussite:</b> %{{y:.1f}}%<br><b>Réussis:</b> %{{customdata[0]}}<br><b>Total:</b> %{{customdata[1]}}<extra></extra>",
        customdata=stats[["Réussis", "Total"]].values,
    )
    
    fig.update_layout(
        yaxis_range=[0, 105],
        xaxis_tickangle=-45,
        xaxis_title=group_col,
        yaxis_title="Taux de réussite (%)",
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        yaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        showlegend=False,
        height=500,
    )
    
    return fig





