# 🎵 Music Trend Visualizer

> A data visualization project built with Python (Streamlit + Plotly) and Spotify API.  
> Analyzes which music genres and audio features dominate streaming trends.

---

## 📁 Project Structure

```
music_trend_viz/
├── app.py                  # Main Streamlit app
├── website.html            # Standalone HTML version (no Python needed)
├── requirements.txt        # Python dependencies
├── .env.example            # Template for API credentials
├── .streamlit/
│   └── config.toml         # Streamlit dark theme config
└── utils/
    ├── __init__.py
    ├── spotify_client.py   # Spotify auth & connection
    ├── data_processor.py   # Data fetching & processing
    └── charts.py           # All Plotly chart functions
```

---

## 🚀 Quick Start

### 1. Clone / Download
```bash
cd music_trend_viz
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Spotify API (optional — app works in demo mode without it)

1. Go to https://developer.spotify.com/dashboard
2. Log in → **Create App**
3. Copy your **Client ID** and **Client Secret**
4. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env and paste your credentials
```

### 4. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 HTML Website Version

The `website.html` file is a fully self-contained website that works without Python.  
Just open it in any browser — no server needed.

Features:
- All 6+ chart types (bar, pie, treemap, histogram, scatter, radar, line)
- Interactive genre filters for Top Tracks
- Refresh button to regenerate data
- Fully responsive design

---

## 📊 Visualizations

| # | Chart | Library | What it shows |
|---|-------|---------|---------------|
| 1 | Bar Chart | Plotly | Top genres by average popularity |
| 2 | Pie/Donut | Plotly | Genre share among trending tracks |
| 3 | Treemap | Plotly | Genre popularity — area = track count |
| 4 | Histogram | Plotly | Tempo (BPM) distribution |
| 5 | Scatter Plot | Plotly | Energy vs Danceability by genre |
| 6 | Line Chart | Plotly | Popularity trend over time periods |
| 7 | Radar Chart | Plotly | Audio feature comparison across genres |

---

## 🔧 Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.10+ |
| Web App | Streamlit |
| Charts | Plotly, (Matplotlib/Seaborn optional) |
| Data | Pandas, NumPy |
| API | Spotify Web API via Spotipy |
| HTML Site | Vanilla JS + Chart.js + D3.js |

---

## 🎛 Audio Features Explained

| Feature | Range | Description |
|---------|-------|-------------|
| Energy | 0–1 | Intensity and activity |
| Danceability | 0–1 | How suitable for dancing |
| Valence | 0–1 | Musical positiveness (happy vs sad) |
| Acousticness | 0–1 | Whether the track is acoustic |
| Tempo | BPM | Speed of the track |
| Speechiness | 0–1 | Presence of spoken words |

---

## 📝 Demo Mode

If no Spotify credentials are provided, the app automatically runs in **Demo Mode** with synthetically generated data that mirrors real Spotify patterns (genre distributions, audio feature ranges, popularity scores).

---

## 📦 Deploying to Streamlit Cloud

1. Push your project to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo → select `app.py`
4. In **Secrets**, add:
```toml
SPOTIPY_CLIENT_ID = "your_client_id"
SPOTIPY_CLIENT_SECRET = "your_client_secret"
```

---

## 👨‍💻 Team

Built as part of a Data Visualization in Python course project.

---

## 📄 License

MIT — free to use and modify.
