from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    playlists = db.relationship("Playlist", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    tracks = db.relationship("Track", backref="playlist", lazy=True)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    spotify_link = db.Column(db.String(300), nullable=False)

    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), nullable=False)


