"""Authentication API (session + CSRF)."""
import re

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def _validate_username(username: str) -> bool:
    return bool(username and _USERNAME_RE.match(username))


def _validate_password(password: str) -> bool:
    return bool(password and len(password) >= 8)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not _validate_username(username):
        return (
            jsonify(
                {
                    "error": "Username must be 3–32 characters: letters, digits, underscore only."
                }
            ),
            400,
        )
    if not _validate_password(password):
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken."}), 409
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return jsonify({"success": True, "user": {"id": user.id, "username": user.username}})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401
    login_user(user, remember=True)
    return jsonify({"success": True, "user": {"id": user.id, "username": user.username}})


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})


@auth_bp.route("/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify(
            {"user": {"id": current_user.id, "username": current_user.username}}
        )
    return jsonify({"user": None})
