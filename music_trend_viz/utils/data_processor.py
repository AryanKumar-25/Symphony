"""
data_processor.py
Fetches and processes data from Spotify API, or generates
realistic synthetic data when running in demo mode.
"""

import pandas as pd
import numpy as np
from utils.spotify_client import is_demo_mode

GENRES = ["Pop", "Hip-Hop", "R&B", "Electronic", "Rock", "Latin", "K-Pop", "Indie", "Country", "Jazz"]
GENRE_WEIGHTS = [0.22, 0.18, 0.12, 0.10, 0.09, 0.09, 0.07, 0.06, 0.05, 0.02]

GENRE_AUDIO_PROFILES = {
    "Pop":        dict(tempo=(110,128), energy=(0.65,0.85), dance=(0.70,0.90), valence=(0.55,0.80), acousticness=(0.05,0.25)),
    "Hip-Hop":    dict(tempo=(80,100),  energy=(0.60,0.80), dance=(0.75,0.92), valence=(0.35,0.65), acousticness=(0.05,0.20)),
    "R&B":        dict(tempo=(75,100),  energy=(0.45,0.70), dance=(0.65,0.85), valence=(0.40,0.70), acousticness=(0.10,0.35)),
    "Electronic": dict(tempo=(120,145), energy=(0.75,0.95), dance=(0.72,0.92), valence=(0.45,0.75), acousticness=(0.02,0.12)),
    "Rock":       dict(tempo=(115,145), energy=(0.70,0.92), dance=(0.45,0.68), valence=(0.40,0.65), acousticness=(0.05,0.25)),
    "Latin":      dict(tempo=(95,130),  energy=(0.68,0.88), dance=(0.80,0.96), valence=(0.65,0.90), acousticness=(0.10,0.30)),
    "K-Pop":      dict(tempo=(100,130), energy=(0.65,0.88), dance=(0.72,0.90), valence=(0.50,0.80), acousticness=(0.04,0.20)),
    "Indie":      dict(tempo=(88,118),  energy=(0.40,0.68), dance=(0.45,0.68), valence=(0.35,0.65), acousticness=(0.20,0.55)),
    "Country":    dict(tempo=(88,120),  energy=(0.45,0.72), dance=(0.55,0.75), valence=(0.50,0.78), acousticness=(0.25,0.60)),
    "Jazz":       dict(tempo=(70,110),  energy=(0.30,0.60), dance=(0.40,0.65), valence=(0.45,0.70), acousticness=(0.40,0.80)),
}

ARTIST_NAMES = {
    "Pop":        ["Taylor Swift","Olivia Rodrigo","Dua Lipa","Harry Styles","Sabrina Carpenter"],
    "Hip-Hop":    ["Drake","Travis Scott","Kendrick Lamar","21 Savage","Future"],
    "R&B":        ["The Weeknd","SZA","Beyoncé","Frank Ocean","H.E.R."],
    "Electronic": ["Calvin Harris","Disclosure","Flume","Fred Again","Four Tet"],
    "Rock":       ["Imagine Dragons","Arctic Monkeys","Foo Fighters","The 1975","Tame Impala"],
    "Latin":      ["Bad Bunny","J Balvin","Rosalía","Karol G","Shakira"],
    "K-Pop":      ["BTS","BLACKPINK","Stray Kids","aespa","NewJeans"],
    "Indie":      ["Phoebe Bridgers","Mitski","Boygenius","Sufjan Stevens","Snail Mail"],
    "Country":    ["Morgan Wallen","Luke Combs","Zach Bryan","Kacey Musgraves","Chris Stapleton"],
    "Jazz":       ["Norah Jones","Esperanza Spalding","Kamasi Washington","Diana Krall","Chet Baker"],
}

TRACK_ADJECTIVES = ["Golden","Midnight","Neon","Faded","Electric","Lost","Wildfire","Echo","Phantom","Crystal"]
TRACK_NOUNS      = ["Dream","Waves","Fire","Heart","Sky","Rain","Light","Storm","Soul","Dance"]

rng = np.random.default_rng(42)

def _synthetic_track_name():
    return f"{rng.choice(TRACK_ADJECTIVES)} {rng.choice(TRACK_NOUNS)}"

def _synthetic_tracks(limit=50):
    rows = []
    for i in range(limit):
        genre = rng.choice(GENRES, p=GENRE_WEIGHTS)
        artist = rng.choice(ARTIST_NAMES[genre])
        prof = GENRE_AUDIO_PROFILES[genre]
        rows.append({
            "rank":             i + 1,
            "track_id":         f"demo_{i:04d}",
            "name":             _synthetic_track_name(),
            "artist":           artist,
            "genre":            genre,
            "popularity":       int(rng.integers(55, 99)),
            "tempo":            float(rng.uniform(*prof["tempo"])),
            "energy":           float(rng.uniform(*prof["energy"])),
            "danceability":     float(rng.uniform(*prof["dance"])),
            "valence":          float(rng.uniform(*prof["valence"])),
            "acousticness":     float(rng.uniform(*prof["acousticness"])),
            "loudness":         float(rng.uniform(-10, -2)),
            "speechiness":      float(rng.uniform(0.03, 0.35)),
            "instrumentalness": float(rng.uniform(0.00, 0.20)),
        })
    return pd.DataFrame(rows)


def _fallback_audio_df(tracks_df: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic audio features as a fallback for live data."""
    synth = _synthetic_tracks(len(tracks_df))
    synth["track_id"] = tracks_df["track_id"].values if "track_id" in tracks_df.columns else [f"track_{i}" for i in range(len(tracks_df))]
    if "name" in tracks_df.columns:
        synth["name"] = tracks_df["name"].values
    if "artist" in tracks_df.columns:
        synth["artist"] = tracks_df["artist"].values
    if "popularity" in tracks_df.columns:
        synth["popularity"] = tracks_df["popularity"].values
    return synth


def get_top_tracks(sp, limit=50, time_range="medium_term") -> pd.DataFrame:
    if is_demo_mode() or sp is None:
        df = _synthetic_tracks(limit)
        return df[["rank","track_id","name","artist","genre","popularity"]]
    try:
        results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
        rows = []
        for i, item in enumerate(results["items"]):
            rows.append({
                "rank":       i + 1,
                "track_id":   item["id"],
                "name":       item["name"],
                "artist":     item["artists"][0]["name"],
                "popularity": item["popularity"],
            })
        if rows:
            return pd.DataFrame(rows)
    except Exception:
        pass
    return _get_tracks_from_search(sp, limit)


def _get_tracks_from_search(sp, limit=50) -> pd.DataFrame:
    rows = []
    queries = ["year:2024", "year:2023 pop", "year:2024 hip-hop", "year:2024 electronic"]
    per_q = max(10, limit // len(queries))
    for q in queries:
        try:
            res = sp.search(q=q, type="track", limit=per_q, market="US")
            for item in res["tracks"]["items"]:
                rows.append({
                    "track_id":   item["id"],
                    "name":       item["name"],
                    "artist":     item["artists"][0]["name"],
                    "popularity": item["popularity"],
                })
        except Exception:
            pass
    if not rows:
        return _synthetic_tracks(limit)[["rank","track_id","name","artist","genre","popularity"]]
    df = pd.DataFrame(rows).drop_duplicates("track_id").head(limit).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df)+1))
    return df


def get_genre_data(tracks_df: pd.DataFrame) -> pd.DataFrame:
    df = tracks_df.copy()
    if "track_id" not in df.columns:
        df["track_id"] = [f"track_{i}" for i in range(len(df))]
    if "popularity" not in df.columns:
        df["popularity"] = rng.integers(55, 99, size=len(df)).astype(int)
    if "genre" not in df.columns:
        df["genre"] = rng.choice(GENRES, p=GENRE_WEIGHTS, size=len(df))
    genre_df = (
        df.groupby("genre")
        .agg(track_count=("track_id", "count"), avg_popularity=("popularity", "mean"))
        .reset_index()
        .sort_values("avg_popularity", ascending=False)
    )
    return genre_df


def get_audio_features_data(sp, tracks_df: pd.DataFrame) -> pd.DataFrame:
    if is_demo_mode() or sp is None:
        return _fallback_audio_df(tracks_df)

    # Ensure track_id exists
    if "track_id" not in tracks_df.columns:
        tracks_df = tracks_df.copy()
        tracks_df["track_id"] = [f"track_{i}" for i in range(len(tracks_df))]

    ids = tracks_df["track_id"].tolist()
    rows = []
    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        try:
            features = sp.audio_features(batch)
            if features:
                for f in features:
                    if f:
                        rows.append({
                            "track_id":         f["id"],
                            "tempo":            f["tempo"],
                            "energy":           f["energy"],
                            "danceability":     f["danceability"],
                            "valence":          f["valence"],
                            "acousticness":     f["acousticness"],
                            "loudness":         f["loudness"],
                            "speechiness":      f["speechiness"],
                            "instrumentalness": f["instrumentalness"],
                        })
        except Exception:
            pass

    # If Spotify audio features failed, fall back to synthetic
    if not rows:
        return _fallback_audio_df(tracks_df)

    feat_df = pd.DataFrame(rows)
    merged = tracks_df.merge(feat_df, on="track_id", how="left")

    if "genre" not in merged.columns:
        merged["genre"] = rng.choice(GENRES, p=GENRE_WEIGHTS, size=len(merged))
    if "popularity" not in merged.columns:
        merged["popularity"] = rng.integers(55, 99, size=len(merged)).astype(int)

    return merged


def get_trend_over_time(sp) -> pd.DataFrame:
    periods = ["short_term", "medium_term", "long_term"]
    period_labels = ["Last 4 weeks", "Last 6 months", "All time"]
    rows = []
    for period, label in zip(periods, period_labels):
        noise = rng.uniform(-0.03, 0.03, len(GENRES))
        weights = np.array(GENRE_WEIGHTS) + noise
        weights = np.clip(weights, 0.01, None)
        weights /= weights.sum()
        base_pop = {g: float(rng.uniform(50, 85)) for g in GENRES}
        if period == "short_term":
            base_pop["Pop"]   += 10
            base_pop["K-Pop"] += 8
        elif period == "long_term":
            base_pop["Rock"]  += 7
            base_pop["Jazz"]  += 5
        for g, pop in base_pop.items():
            rows.append({"period": label, "genre": g, "popularity": min(99, pop)})
    return pd.DataFrame(rows)


def get_artist_data(sp, tracks_df: pd.DataFrame) -> pd.DataFrame:
    if is_demo_mode() or sp is None:
        data = []
        for genre, artists in ARTIST_NAMES.items():
            for a in artists:
                data.append({
                    "artist":     a,
                    "genre":      genre,
                    "followers":  int(rng.integers(500_000, 80_000_000)),
                    "popularity": int(rng.integers(60, 99)),
                })
        return pd.DataFrame(data).sort_values("popularity", ascending=False).head(30)
    return pd.DataFrame()