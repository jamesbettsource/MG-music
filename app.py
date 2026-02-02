from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

from models import db, Playlist, Track

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///playlist.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
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
            playlist_id=playlist.id
        )
        db.session.add(track)

    db.session.commit()

    return jsonify({
        "playlist_id": playlist.id,
        "genre": genre,
        "tracks": spotify_tracks
    })


