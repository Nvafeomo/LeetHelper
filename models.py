"""SQLAlchemy models."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    attempts = db.relationship(
        "Attempt", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Attempt(db.Model):
    __tablename__ = "attempts"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "problem_id", "attempt_label", name="uq_user_problem_attempt"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    problem_id = db.Column(db.Integer, nullable=False, index=True)
    attempt_label = db.Column(db.String(32), nullable=False)
    time_spent = db.Column(db.String(255), default="")
    approach = db.Column(db.Text, default="")
    reflection = db.Column(db.Text, default="")
    solved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def to_note_dict(self) -> dict:
        ts = ""
        if self.created_at:
            ts = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "attempt": self.attempt_label,
            "timestamp": ts,
            "time_spent": self.time_spent or "",
            "approach": self.approach or "",
            "reflection": self.reflection or "",
            "solved": bool(self.solved),
        }
