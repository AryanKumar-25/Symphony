"""
charts.py
All Plotly visualization functions for the Music Trend Visualizer.
Dark-themed, Spotify-style aesthetic throughout.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Design tokens ──────────────────────────────────────────────────────────────
BG        = "rgba(0,0,0,0)"
PAPER_BG  = "rgba(13,13,26,0.0)"
GRID_CLR  = "rgba(255,255,255,0.07)"
TEXT_CLR  = "#c0c0cc"
SPOTIFY   = "#1DB954"

GENRE_PALETTE = {
    "Pop":        "#1DB954",
    "Hip-Hop":    "#FF6B6B",
    "R&B":        "#A855F7",
    "Electronic": "#06B6D4",
    "Rock":       "#F59E0B",
    "Latin":      "#EC4899",
    "K-Pop":      "#8B5CF6",
    "Indie":      "#6EE7B7",
    "Country":    "#FCD34D",
    "Jazz":       "#93C5FD",
}

def _base_layout(**kwargs) -> dict:
    return dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=BG,
        font=dict(family="DM Sans, sans-serif", color=TEXT_CLR, size=13),
        margin=dict(l=20, r=20, t=40, b=20),
        **kwargs
    )


def _axis(title="", **kwargs):
    return dict(
        title=title,
        gridcolor=GRID_CLR,
        linecolor=GRID_CLR,
        tickcolor=GRID_CLR,
        **kwargs
    )


# ── 1. Genre Bar Chart ─────────────────────────────────────────────────────────
def plot_genre_bar(genre_df: pd.DataFrame) -> go.Figure:
    top = genre_df.sort_values("avg_popularity", ascending=False).head(10)
    colors = [GENRE_PALETTE.get(g, SPOTIFY) for g in top["genre"]]

    fig = go.Figure(go.Bar(
        x=top["genre"],
        y=top["avg_popularity"],
        marker=dict(
            color=colors,
            line=dict(color="rgba(0,0,0,0)", width=0),
            cornerradius=6,
        ),
        hovertemplate="<b>%{x}</b><br>Avg Popularity: %{y:.1f}<extra></extra>",
        text=top["avg_popularity"].round(1),
        textposition="outside",
        textfont=dict(color=TEXT_CLR, size=11),
    ))

    fig.update_layout(
        **_base_layout(height=320),
        xaxis=_axis(),
        yaxis=_axis("Avg Popularity", range=[0, 105]),
        showlegend=False,
        bargap=0.3,
    )
    return fig


# ── 2. Genre Pie / Donut Chart ─────────────────────────────────────────────────
def plot_genre_pie(genre_df: pd.DataFrame) -> go.Figure:
    top = genre_df.head(8)
    colors = [GENRE_PALETTE.get(g, SPOTIFY) for g in top["genre"]]

    fig = go.Figure(go.Pie(
        labels=top["genre"],
        values=top["track_count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a0a0f", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} tracks (%{percent})<extra></extra>",
        textinfo="percent",
        textfont=dict(size=11, color="#fff"),
    ))

    fig.update_layout(
        **_base_layout(height=320),
        legend=dict(
            font=dict(color=TEXT_CLR, size=11),
            bgcolor="rgba(0,0,0,0)",
            x=1.0,
        ),
        annotations=[dict(
            text="Genre<br>Share",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_CLR),
        )]
    )
    return fig


# ── 3. Treemap ──────────────────────────────────────────────────────────────────
def plot_treemap(genre_df: pd.DataFrame) -> go.Figure:
    colors = [GENRE_PALETTE.get(g, SPOTIFY) for g in genre_df["genre"]]

    fig = go.Figure(go.Treemap(
        labels=genre_df["genre"],
        parents=[""] * len(genre_df),
        values=genre_df["track_count"],
        customdata=genre_df[["avg_popularity"]].round(1),
        hovertemplate="<b>%{label}</b><br>Tracks: %{value}<br>Avg Popularity: %{customdata[0]}<extra></extra>",
        marker=dict(
            colors=colors,
            line=dict(width=2, color="#0a0a0f"),
        ),
        textinfo="label+value",
        textfont=dict(size=13, color="#fff"),
    ))

    fig.update_layout(**_base_layout(height=380))
    return fig


# ── 4. Tempo Histogram ─────────────────────────────────────────────────────────
def plot_tempo_histogram(audio_df: pd.DataFrame) -> go.Figure:
    tempos = audio_df["tempo"].dropna()

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=tempos,
        nbinsx=30,
        marker=dict(
            color=SPOTIFY,
            line=dict(color="#0a0a0f", width=1),
            opacity=0.85,
        ),
        hovertemplate="BPM: %{x:.0f}<br>Count: %{y}<extra></extra>",
    ))

    # Mean line
    mean_bpm = tempos.mean()
    fig.add_vline(
        x=mean_bpm, line_dash="dash",
        line_color="#FF6B6B", line_width=1.5,
        annotation_text=f"Mean: {mean_bpm:.0f} BPM",
        annotation_font_color="#FF6B6B",
        annotation_font_size=11,
    )

    fig.update_layout(
        **_base_layout(height=300),
        xaxis=_axis("Tempo (BPM)"),
        yaxis=_axis("Track Count"),
        showlegend=False,
        bargap=0.05,
    )
    return fig


# ── 5. Scatter — Energy vs Danceability ────────────────────────────────────────
def plot_scatter_energy_dance(audio_df: pd.DataFrame) -> go.Figure:
    df = audio_df.dropna(subset=["energy", "danceability"])

    fig = go.Figure()

    genres = df["genre"].unique() if "genre" in df.columns else ["Unknown"]
    for genre in genres:
        g_df = df[df["genre"] == genre] if "genre" in df.columns else df
        fig.add_trace(go.Scatter(
            x=g_df["energy"],
            y=g_df["danceability"],
            mode="markers",
            name=genre,
            marker=dict(
                color=GENRE_PALETTE.get(genre, SPOTIFY),
                size=7,
                opacity=0.75,
                line=dict(color="rgba(0,0,0,0.3)", width=0.5),
            ),
            hovertemplate=(
                f"<b>{genre}</b><br>"
                "Energy: %{x:.2f}<br>"
                "Danceability: %{y:.2f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        **_base_layout(height=300),
        xaxis=_axis("Energy", range=[0, 1]),
        yaxis=_axis("Danceability", range=[0, 1]),
        legend=dict(
            font=dict(color=TEXT_CLR, size=10),
            bgcolor="rgba(13,13,26,0.7)",
            bordercolor=GRID_CLR,
            borderwidth=1,
        ),
    )
    return fig


# ── 6. Trend Line ──────────────────────────────────────────────────────────────
def plot_trend_line(trend_df: pd.DataFrame) -> go.Figure:
    periods_order = ["Last 4 weeks", "Last 6 months", "All time"]
    fig = go.Figure()

    top_genres = (
        trend_df.groupby("genre")["popularity"]
        .mean()
        .sort_values(ascending=False)
        .head(7)
        .index.tolist()
    )

    for genre in top_genres:
        g_df = trend_df[trend_df["genre"] == genre].copy()
        g_df["period"] = pd.Categorical(g_df["period"], categories=periods_order, ordered=True)
        g_df = g_df.sort_values("period")
        color = GENRE_PALETTE.get(genre, SPOTIFY)

        fig.add_trace(go.Scatter(
            x=g_df["period"],
            y=g_df["popularity"],
            mode="lines+markers",
            name=genre,
            line=dict(color=color, width=2.5),
            marker=dict(color=color, size=8, line=dict(color="#0a0a0f", width=2)),
            hovertemplate=f"<b>{genre}</b><br>%{{x}}<br>Popularity: %{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(height=340),
        xaxis=_axis("Time Period"),
        yaxis=_axis("Avg Popularity", range=[40, 100]),
        legend=dict(
            font=dict(color=TEXT_CLR, size=11),
            bgcolor="rgba(13,13,26,0.7)",
            bordercolor=GRID_CLR,
            borderwidth=1,
            orientation="h",
            x=0, y=-0.25,
        ),
        hovermode="x unified",
    )
    return fig


# ── 7. Audio Feature Radar ─────────────────────────────────────────────────────
def plot_audio_radar(audio_df: pd.DataFrame, selected_genres: list) -> go.Figure:
    features = ["energy", "danceability", "valence", "acousticness", "speechiness"]
    feature_labels = ["Energy", "Danceability", "Valence", "Acousticness", "Speechiness"]

    fig = go.Figure()

    for genre in selected_genres:
        g_df = audio_df[audio_df["genre"] == genre] if "genre" in audio_df.columns else audio_df
        vals = [g_df[f].mean() for f in features if f in g_df.columns]
        if len(vals) < len(features):
            continue
        vals += [vals[0]]   # close the polygon
        color = GENRE_PALETTE.get(genre, SPOTIFY)

        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=feature_labels + [feature_labels[0]],
            name=genre,
            line=dict(color=color, width=2),
            fill="toself",
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
            marker=dict(color=color),
            hovertemplate=f"<b>{genre}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(height=420),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color=TEXT_CLR, size=9),
                gridcolor=GRID_CLR,
                linecolor=GRID_CLR,
            ),
            angularaxis=dict(
                tickfont=dict(color=TEXT_CLR, size=12),
                gridcolor=GRID_CLR,
                linecolor=GRID_CLR,
            ),
        ),
        legend=dict(
            font=dict(color=TEXT_CLR, size=11),
            bgcolor="rgba(13,13,26,0.7)",
            bordercolor=GRID_CLR,
        ),
    )
    return fig


# ── 8. Popularity Heatmap (bonus) ──────────────────────────────────────────────
def plot_popularity_heatmap(audio_df: pd.DataFrame) -> go.Figure:
    features = ["energy", "danceability", "valence", "acousticness", "tempo"]
    existing = [f for f in features if f in audio_df.columns]

    if "genre" not in audio_df.columns or len(existing) < 2:
        return go.Figure()

    matrix = audio_df.groupby("genre")[existing].mean().round(3)

    # Normalize tempo to 0-1 scale
    if "tempo" in matrix.columns:
        matrix["tempo"] = (matrix["tempo"] - matrix["tempo"].min()) / (matrix["tempo"].max() - matrix["tempo"].min() + 1e-9)

    fig = go.Figure(go.Heatmap(
        z=matrix.values,
        x=[c.capitalize() for c in matrix.columns],
        y=matrix.index.tolist(),
        colorscale=[[0, "#0a0a0f"], [0.5, "#1DB95480"], [1, "#1DB954"]],
        hovertemplate="Genre: %{y}<br>Feature: %{x}<br>Value: %{z:.2f}<extra></extra>",
        text=matrix.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=11, color="#fff"),
    ))

    fig.update_layout(
        **_base_layout(height=380),
        xaxis=dict(side="top", tickfont=dict(color=TEXT_CLR)),
        yaxis=dict(tickfont=dict(color=TEXT_CLR)),
    )
    return fig