"""
Histogrammes de notes avec Plotly.

Les fonctions de ce module produisent des graphiques plus pédagogiques :
- histogramme global avec ligne verticale sur la moyenne et le seuil de réussite ;
- histogramme comparant plusieurs groupes (départements, niveaux, etc.).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def grade_histogram(
    df: pd.DataFrame,
    title: str = "Distribution des notes",
    pass_threshold: float = 10.0,
) -> go.Figure:
    """
    Crée un histogramme global des notes avec :
    - une ligne verticale pour la moyenne,
    - une ligne verticale pour le seuil de réussite.

    Parameters
    ----------
    df : DataFrame avec colonne `grade`
    title : titre du graphique
    pass_threshold : seuil de réussite (par défaut 10/20)
    """
    fig = px.histogram(
        df,
        x="grade",
        nbins=30,
        marginal="box",
        opacity=0.85,
        title=title,
        labels={"grade": "Note (/20)", "count": "Nombre d'étudiants"},
        color_discrete_sequence=["#2E86AB"],
    )

    mean_val = df["grade"].mean()
    median_val = df["grade"].median()
    std_val = df["grade"].std()
    
    # Zone de réussite (vert clair)
    fig.add_vrect(
        x0=pass_threshold,
        x1=20,
        fillcolor="green",
        opacity=0.1,
        layer="below",
        line_width=0,
        annotation_text="Zone de réussite",
        annotation_position="top left",
    )
    
    # Zone d'échec (rouge clair)
    fig.add_vrect(
        x0=0,
        x1=pass_threshold,
        fillcolor="red",
        opacity=0.1,
        layer="below",
        line_width=0,
        annotation_text="Zone d'échec",
        annotation_position="top left",
    )

    # Ligne verticale sur la moyenne
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_width=2.5,
        line_color="#06A77D",
        annotation_text=f"Moyenne = {mean_val:.2f}/20",
        annotation_position="top left",
        annotation=dict(font_size=12, font_color="#06A77D", bgcolor="rgba(240,240,240,0.9)", bordercolor="#06A77D", borderwidth=1),
    )
    
    # Ligne verticale sur la médiane
    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_width=2,
        line_color="#F18F01",
        annotation_text=f"Médiane = {median_val:.2f}/20",
        annotation_position="top right",
        annotation=dict(font_size=12, font_color="#F18F01", bgcolor="rgba(240,240,240,0.9)", bordercolor="#F18F01", borderwidth=1),
    )

    # Ligne verticale sur le seuil de réussite
    fig.add_vline(
        x=pass_threshold,
        line_dash="solid",
        line_width=3,
        line_color="#C73E1D",
        annotation_text=f"Seuil de réussite = {pass_threshold}/20",
        annotation_position="top",
        annotation=dict(font_size=13, font_color="#C73E1D", bgcolor="rgba(240,240,240,0.9)", bordercolor="#C73E1D", borderwidth=2, font=dict(weight="bold")),
    )

    # Calcul du taux de réussite pour l'annotation
    pass_rate = (df["grade"] >= pass_threshold).sum() / len(df) * 100
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>Taux de réussite : {pass_rate:.1f}%</b><br>Effectif total : {len(df)} étudiants",
        showarrow=False,
        align="left",
        bgcolor="rgba(240,240,240,0.9)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=11),
    )

    fig.update_layout(
        bargap=0.05,
        hovermode="x unified",
        xaxis_title="Note (/20)",
        yaxis_title="Nombre d'étudiants",
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        yaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
    )
    
    # Améliorer les tooltips
    fig.update_traces(
        hovertemplate="<b>Note :</b> %{x:.2f}/20<br><b>Effectif :</b> %{y} étudiants<extra></extra>"
    )
    
    return fig


def grade_histogram_by_group(
    df: pd.DataFrame,
    group_col: str,
    title: str = "Distribution des notes par groupe",
    pass_threshold: float = 10.0,
) -> go.Figure:
    """
    Histogramme des notes avec une couleur par groupe (département, niveau, etc.).
    Inclut des lignes de référence pour la moyenne et le seuil de réussite.

    Parameters
    ----------
    df : DataFrame avec colonne `grade`
    group_col : colonne de groupement (ex. department, level)
    title : titre du graphique
    pass_threshold : seuil de réussite (par défaut 10/20)
    """
    fig = px.histogram(
        df,
        x="grade",
        color=group_col,
        nbins=30,
        barmode="overlay",
        opacity=0.65,
        title=title,
        labels={"grade": "Note (/20)", group_col: group_col, "count": "Nombre d'étudiants"},
    )
    
    # Zone de réussite
    fig.add_vrect(
        x0=pass_threshold,
        x1=20,
        fillcolor="green",
        opacity=0.08,
        layer="below",
        line_width=0,
    )
    
    # Zone d'échec
    fig.add_vrect(
        x0=0,
        x1=pass_threshold,
        fillcolor="red",
        opacity=0.08,
        layer="below",
        line_width=0,
    )
    
    # Ligne du seuil de réussite
    fig.add_vline(
        x=pass_threshold,
        line_dash="solid",
        line_width=2.5,
        line_color="#C73E1D",
        annotation_text=f"Seuil = {pass_threshold}/20",
        annotation_position="top",
        annotation=dict(font_size=11, font_color="#C73E1D", bgcolor="rgba(240,240,240,0.9)", bordercolor="#C73E1D", borderwidth=1),
    )
    
    # Moyenne globale
    mean_val = df["grade"].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_width=2,
        line_color="black",
        annotation_text=f"Moyenne globale = {mean_val:.2f}/20",
        annotation_position="bottom",
        annotation=dict(font_size=10, bgcolor="rgba(240,240,240,0.9)", bordercolor="black", borderwidth=1),
    )
    
    # Calcul des statistiques par groupe pour l'annotation
    groups = df[group_col].unique()
    stats_text = "<b>Statistiques par groupe :</b><br>"
    for group in sorted(groups):
        group_df = df[df[group_col] == group]
        group_mean = group_df["grade"].mean()
        group_pass_rate = (group_df["grade"] >= pass_threshold).sum() / len(group_df) * 100
        stats_text += f"• {group}: Moyenne={group_mean:.2f}, Réussite={group_pass_rate:.1f}%<br>"
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=stats_text,
        showarrow=False,
        align="left",
        bgcolor="rgba(240,240,240,0.9)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=10),
    )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Note (/20)",
        yaxis_title="Nombre d'étudiants",
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        yaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        legend=dict(title=group_col, yanchor="top", y=0.99, xanchor="left", x=1.01, bgcolor="rgba(240,240,240,0.9)"),
    )
    
    # Améliorer les tooltips
    fig.update_traces(
        hovertemplate=f"<b>{group_col}:</b> %{{fullData.name}}<br><b>Note :</b> %{{x:.2f}}/20<br><b>Effectif :</b> %{{y}} étudiants<extra></extra>"
    )
    
    return fig





