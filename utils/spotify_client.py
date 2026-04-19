"""
spotify_client.py
Handles Spotify authentication via Spotipy.
Falls back to demo mode if no credentials are found.
"""

import os
import streamlit as st

_demo = False

def is_demo_mode() -> bool:
    return _demo

def get_spotify_client():
    """Return an authenticated Spotipy client, or None in demo mode."""
    global _demo

    # 1. Try Streamlit secrets (cloud deployment)
    try:
        client_id     = st.secrets["SPOTIPY_CLIENT_ID"]
        client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
    except Exception:
        # 2. Fall back to environment variables / .env file
        from dotenv import load_dotenv
        load_dotenv()
        client_id     = os.getenv("SPOTIPY_CLIENT_ID", "")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        _demo = True
        return None          # data_processor will generate synthetic data

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        auth = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth)
        sp.search(q="test", limit=1)   # quick connectivity check
        _demo = False
        return sp
    except Exception as e:
        st.warning(f"Spotify connection failed ({e}). Running in demo mode.")
        _demo = True
        return None
