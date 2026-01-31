from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

from models import db   # import database

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# ---------------- DATABASE CONFIG (HERE ✅) ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
# -----------------------------------------------------------

# Spotify Authentication
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)

def get_tracks_by_genre(genre, limit=10):
    results = spotify.search(q=f'genre:{genre}', type='track', limit=limit)
    tracks = []

    for item in results['tracks']['items']:
        tracks.append({
            "song": item['name'],
            "artist": item['artists'][0]['name'],
            "link": item['external_urls']['spotify']
        })
    return tracks

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    data = request.json
    genre = data.get("genre")

    if not genre:
        return jsonify({"error": "Genre is required"}), 400

    spotify_tracks = get_tracks_by_genre(genre)

    # Save playlist
    playlist = Playlist(genre=genre)
    db.session.add(playlist)
    db.session.commit()

    # Save tracks
    for t in spotify_tracks:
        track = Track(
            song_name=t["song"],
            artist=t["artist"],
            spotify_link=t["link"],
            playlist_id=playlist.id
        )
        db.session.add(track)

    db.session.commit()

    return jsonify({
        "playlist_id": playlist.id,
        "genre": genre,
        "tracks": spotify_tracks
    })

