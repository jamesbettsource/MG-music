from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

from models import db, Playlist, Track


def create_app():
    app = Flask(__name__)

    # ---- DATABASE CONFIG (RENDER SAFE) ----
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    # Force psycopg v3 (important!)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app


app = create_app()


# ---- SPOTIFY CLIENT ----
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    )
)


def get_tracks_by_genre(genre, limit=10):
    results = spotify.search(q=f"genre:{genre}", type="track", limit=limit)

    tracks = []
    for item in results["tracks"]["items"]:
        tracks.append({
            "song": item["name"],
            "artist": item["artists"][0]["name"],
            "link": item["external_urls"]["spotify"],
        })

    return tracks


@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    data = request.get_json()
    genre = data.get("genre") if data else None

    if not genre:
        return jsonify({"error": "Genre is required"}), 400

    spotify_tracks = get_tracks_by_genre(genre)

    playlist = Playlist(genre=genre)
    db.session.add(playlist)
    db.session.commit()

    for t in spotify_tracks:
        track = Track(
            song_name=t["song"],
            artist=t["artist"],
            spotify_link=t["link"],
            playlist_id=playlist.id,
        )
        db.session.add(track)

    db.session.commit()

    return jsonify({
        "playlist_id": playlist.id,
        "genre": genre,
        "tracks": spotify_tracks,
    })




