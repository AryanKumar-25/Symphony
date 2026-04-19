import streamlit as st

st.set_page_config(
    page_title="Symphony",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background: #0a0a0f; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #080810 100%); }

    .hero-title {
        font-family: 'Space Mono', monospace;
        font-size: 3.2rem; font-weight: 700;
        background: linear-gradient(90deg, #1DB954, #1ed760, #7CFC00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; letter-spacing: -1px; line-height: 1.1;
    }
    .hero-sub { font-size: 1.15rem; color: #a8a8b3; font-weight: 300; margin-top: 0.5rem; }
    .metric-card {
        background: rgba(29,185,84,0.06); border: 1px solid rgba(29,185,84,0.2);
        border-radius: 16px; padding: 1.5rem; text-align: center;
    }
    .metric-num { font-family: 'Space Mono', monospace; font-size: 2.4rem; font-weight: 700; color: #1DB954; }
    .metric-label { font-size: 0.85rem; color: #a8a8b3; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
    .section-header {
        font-family: 'Space Mono', monospace; font-size: 1.1rem; color: #1DB954;
        letter-spacing: 0.05em; margin-bottom: 1rem; padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(29,185,84,0.2);
    }
    .stSelectbox label, .stSlider label, .stMultiSelect label { color: #c0c0cc !important; font-size: 0.9rem; }
    div[data-testid="stSidebar"] { background: rgba(13,13,26,0.95) !important; border-right: 1px solid rgba(29,185,84,0.15); }
    .sidebar-brand { font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #1DB954; padding: 1rem 0; border-bottom: 1px solid rgba(29,185,84,0.2); margin-bottom: 1rem; }
    .stButton>button {
        background: linear-gradient(135deg, #1DB954, #17a349); color: #000;
        font-weight: 600; border: none; border-radius: 50px; padding: 0.6rem 2rem;
        font-size: 0.95rem; letter-spacing: 0.02em; transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(29,185,84,0.35); }
    .info-box {
        background: rgba(29,185,84,0.07); border-left: 3px solid #1DB954;
        border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin: 1rem 0;
        color: #c0c0cc; font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

from utils.spotify_client import get_spotify_client, is_demo_mode
from utils.data_processor import (
    get_top_tracks, get_genre_data, get_audio_features_data,
    get_trend_over_time, get_artist_data
)
from utils.charts import (
    plot_genre_bar, plot_genre_pie, plot_treemap,
    plot_tempo_histogram, plot_scatter_energy_dance,
    plot_trend_line, plot_audio_radar, plot_popularity_heatmap
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🎵 Symphony</div>', unsafe_allow_html=True)
    st.markdown("### Settings")
    market = st.selectbox("Market / Region", ["Global","US","IN","GB","DE","BR","JP"])
    time_range = st.selectbox("Time Range",
        ["short_term","medium_term","long_term"],
        format_func=lambda x: {"short_term":"Last 4 weeks","medium_term":"Last 6 months","long_term":"All time"}[x])
    limit = st.slider("Number of Tracks", 20, 100, 50, step=10)
    st.markdown("---")
    st.markdown("### Visualizations")
    show_bar     = st.checkbox("Genre Bar Chart", True)
    show_pie     = st.checkbox("Genre Pie Chart", True)
    show_tree    = st.checkbox("Treemap", True)
    show_hist    = st.checkbox("Tempo Histogram", True)
    show_scatter = st.checkbox("Energy vs Danceability", True)
    show_line    = st.checkbox("Trend Over Time", True)
    show_radar   = st.checkbox("Audio Feature Radar", True)
    st.markdown("---")
    refresh = st.button("🔄 Refresh Data")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Symphony</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Discover what\'s dominating Spotify — powered by real audio feature data</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if is_demo_mode():
    st.markdown("""
    <div class="info-box">
    ⚡ <strong>Running in Demo Mode</strong> — showing synthetic data that mirrors real Spotify patterns.
    Add your <code>SPOTIPY_CLIENT_ID</code> and <code>SPOTIPY_CLIENT_SECRET</code> to Streamlit secrets to connect live data.
    </div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching data from Spotify..."):
    sp        = get_spotify_client()
    tracks_df = get_top_tracks(sp, limit=limit, time_range=time_range)
    genre_df  = get_genre_data(tracks_df)
    audio_df  = get_audio_features_data(sp, tracks_df)
    trend_df  = get_trend_over_time(sp)
    artist_df = get_artist_data(sp, tracks_df)

# Guarantee audio_df is never None
if audio_df is None or len(audio_df) == 0:
    from utils.data_processor import _fallback_audio_df
    audio_df = _fallback_audio_df(tracks_df)

# ── KPI Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(tracks_df)}</div><div class="metric-label">Tracks Analysed</div></div>', unsafe_allow_html=True)
with c2:
    top_genre = genre_df.iloc[0]["genre"] if len(genre_df) > 0 else "—"
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="font-size:1.4rem;">{top_genre}</div><div class="metric-label">Top Genre</div></div>', unsafe_allow_html=True)
with c3:
    avg_pop = int(tracks_df["popularity"].mean()) if "popularity" in tracks_df.columns and len(tracks_df) > 0 else 0
    st.markdown(f'<div class="metric-card"><div class="metric-num">{avg_pop}</div><div class="metric-label">Avg Popularity</div></div>', unsafe_allow_html=True)
with c4:
    n_genres = genre_df["genre"].nunique() if "genre" in genre_df.columns else 0
    st.markdown(f'<div class="metric-card"><div class="metric-num">{n_genres}</div><div class="metric-label">Genres Found</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
if show_bar or show_pie:
    col1, col2 = st.columns([3, 2])
    with col1:
        if show_bar:
            st.markdown('<div class="section-header">TOP GENRES BY POPULARITY</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_genre_bar(genre_df), use_container_width=True)
    with col2:
        if show_pie:
            st.markdown('<div class="section-header">GENRE SHARE</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_genre_pie(genre_df), use_container_width=True)

if show_tree:
    st.markdown('<div class="section-header">GENRE TREEMAP — SIZE = TRACK COUNT</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_treemap(genre_df), use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
if show_hist or show_scatter:
    col1, col2 = st.columns(2)
    with col1:
        if show_hist:
            st.markdown('<div class="section-header">TEMPO DISTRIBUTION (BPM)</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_tempo_histogram(audio_df), use_container_width=True)
    with col2:
        if show_scatter:
            st.markdown('<div class="section-header">ENERGY vs DANCEABILITY</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_scatter_energy_dance(audio_df), use_container_width=True)

if show_line:
    st.markdown('<div class="section-header">GENRE POPULARITY TREND OVER TIME</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_trend_line(trend_df), use_container_width=True)

if show_radar:
    st.markdown('<div class="section-header">AUDIO FEATURES BY GENRE</div>', unsafe_allow_html=True)
    genres_available = audio_df["genre"].unique().tolist() if "genre" in audio_df.columns else []
    selected_genres = st.multiselect(
        "Select genres to compare",
        options=genres_available,
        default=genres_available[:4] if len(genres_available) >= 4 else genres_available
    )
    if selected_genres:
        st.plotly_chart(plot_audio_radar(audio_df, selected_genres), use_container_width=True)

# ── Top Tracks Table ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">TOP TRACKS DATA</div>', unsafe_allow_html=True)
with st.expander("View full dataset", expanded=False):
    merged = tracks_df.copy()
    extra_cols = [c for c in ["tempo","energy","danceability","valence","acousticness","genre"] if c in audio_df.columns]
    if extra_cols and "track_id" in audio_df.columns:
        merged = merged.merge(
            audio_df[["track_id"] + extra_cols].drop_duplicates("track_id"),
            on="track_id", how="left"
        )
    st.dataframe(merged.head(50), use_container_width=True, height=400)
    csv = merged.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "symphony_tracks.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#555566; font-size:0.8rem; padding:1rem 0;">
    Built with ❤️ using Python · Streamlit · Plotly · Spotipy &nbsp;|&nbsp; Symphony — Data Visualization Project
</div>
""", unsafe_allow_html=True)