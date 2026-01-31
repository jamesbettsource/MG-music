from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
