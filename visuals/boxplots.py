"""
Boxplots de notes avec Plotly.
"""

import pandas as pd
import plotly.express as px


def grade_boxplot_by(
    df: pd.DataFrame,
    group_col: str,
    title: str = "Distribution des notes par groupe",
    pass_threshold: float = 10.0,
):
    """
    Crée un boxplot des notes par groupe avec des annotations explicatives.

    Parameters
    ----------
    df : DataFrame avec colonne `grade`
    group_col : colonne de groupement (ex. department, program, level, subject_name)
    pass_threshold : seuil de réussite (par défaut 10/20)
    """
    fig = px.box(
        df,
        x=group_col,
        y="grade",
        title=title,
        labels={"grade": "Note (/20)", group_col: group_col},
        color=group_col,
    )
    
    # Zone de réussite
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
    
    # Calcul des statistiques par groupe
    groups = df[group_col].unique()
    stats_text = "<b>Statistiques par groupe :</b><br>"
    for group in sorted(groups):
        group_df = df[df[group_col] == group]
        group_mean = group_df["grade"].mean()
        group_median = group_df["grade"].median()
        group_pass_rate = (group_df["grade"] >= pass_threshold).sum() / len(group_df) * 100
        stats_text += f"• {group}: Moy={group_mean:.2f}, Méd={group_median:.2f}, Réussite={group_pass_rate:.1f}%<br>"
    
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
        xaxis_tickangle=-45,
        xaxis_title=group_col,
        yaxis_title="Note (/20)",
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        yaxis=dict(gridcolor="rgba(200,200,200,0.3)", linecolor="gray", showgrid=True),
        showlegend=False,
        height=600,
    )
    
    # Améliorer les tooltips
    fig.update_traces(
        hovertemplate=f"<b>{group_col}:</b> %{{x}}<br><b>Note:</b> %{{y:.2f}}/20<extra></extra>"
    )
    
    return fig







