from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Playlist(db.Model):
    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)

    tracks = db.relationship("Track", backref="playlist", lazy=True)


class Track(db.Model):
    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    spotify_link = db.Column(db.String(300), nullable=False)

    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey("playlists.id"),
        nullable=False
    )
