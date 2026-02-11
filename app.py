from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import os

from models import db, User


def create_app():
    app = Flask(__name__)

    # Allow your React frontend (Netlify) to talk to backend
    CORS(app)

    # ---------------- CONFIG ----------------

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    # Fix Render Postgres URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    # ---------------- ROOT ----------------

    @app.route("/")
    def index():
        return jsonify(
            service="mg-music-backend",
            status="running"
        )

    # ---------------- AUTH API ----------------

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json()

        if not data:
            return jsonify(error="Missing JSON body"), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify(error="Email and password required"), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify(error="Invalid credentials"), 401

        token = create_access_token(identity=str(user.id))

        return jsonify(access_token=token)

    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json()

        if not data:
            return jsonify(error="Missing JSON body"), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify(error="Email and password required"), 400

        if User.query.filter_by(email=email).first():
            return jsonify(error="User already exists"), 400

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return jsonify(message="User registered successfully"), 201

    # ---------------- PROTECTED API ----------------

    @app.route("/api/songs", methods=["POST"])
    @jwt_required()
    def get_songs():
        user_id = get_jwt_identity()
        data = request.get_json()

        genre = data.get("genre") if data else None

        if not genre:
            return jsonify(error="Genre is required"), 400

        return jsonify(
            user_id=user_id,
            genre=genre,
            songs=[
                f"{genre} Anthem",
                f"{genre} Vibes",
                f"{genre} Night Session"
            ]
        )

    # ---------------- HEALTH ----------------

    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()












