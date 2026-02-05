from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

from models import db, User, Playlist, Track


def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---- DATABASE ----
    database_url = os.getenv("DATABASE_URL")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- JWT ----
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

# ---- SPOTIFY ----
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    )
)


# ---------- FRONTEND ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


# ---------- AUTH ----------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User exists"}), 400

    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token})


# ---------- PLAYLIST ----------
@app.route("/api/generate_playlist", methods=["POST"])
@jwt_required()
def generate_playlist():
    user_id = get_jwt_identity()
    genre = request.json.get("genre")

    results = spotify.search(q=f"genre:{genre}", type="track", limit=10)

    playlist = Playlist(genre=genre, user_id=user_id)
    db.session.add(playlist)
    db.session.commit()

    tracks = []
    for item in results["tracks"]["items"]:
        track = Track(
            song_name=item["name"],
            artist=item["artists"][0]["name"],
            spotify_link=item["external_urls"]["spotify"],
            playlist_id=playlist.id,
        )
        db.session.add(track)
        tracks.append({
            "song": track.song_name,
            "artist": track.artist,
            "link": track.spotify_link,
        })

    db.session.commit()

    return jsonify({"genre": genre, "tracks": tracks})







