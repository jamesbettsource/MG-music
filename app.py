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

    # CORS — allow frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CONFIG
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret")

    database_url = os.environ.get("DATABASE_URL")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if User.query.filter_by(email=email).first():
            return jsonify(error="User exists"), 400

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify(message="Registered"), 201

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json()
        user = User.query.filter_by(email=data.get("email")).first()

        if not user or not user.check_password(data.get("password")):
            return jsonify(error="Invalid credentials"), 401

        token = create_access_token(identity=str(user.id))
        return jsonify(access_token=token)

    @app.route("/api/songs", methods=["POST"])
    @jwt_required()
    def songs():
        data = request.get_json()
        genre = data.get("genre")

        if not genre:
            return jsonify(error="Genre required"), 400

        return jsonify(
            songs=[
                f"{genre} Anthem",
                f"{genre} Vibes",
                f"{genre} Night Session"
            ]
        )

    return app


app = create_app()












