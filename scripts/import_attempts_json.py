"""
Import legacy data/attempts.json into the SQL database for a user.

Usage (from repo root):
  python scripts/import_attempts_json.py USERNAME [path/to/attempts.json]

Default path is data/attempts.json. Skips if a row already exists for the same
(user_id, problem_id, attempt_label).
"""
import os
import sys
from datetime import datetime

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app import app  # noqa: E402
from extensions import db  # noqa: E402
from models import Attempt, User  # noqa: E402
from utils.storage import load_attempts  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_attempts_json.py USERNAME [attempts.json]")
        sys.exit(1)
    username = sys.argv[1].strip()
    path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_ROOT, "data", "attempts.json")
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User not found: {username!r} — register in the app first.")
            sys.exit(1)
        data = load_attempts(path)
        n = 0
        for pid, entry in data.items():
            for note in entry.get("attempts") or []:
                label = str(note.get("attempt") or "")
                if not label:
                    continue
                exists = Attempt.query.filter_by(
                    user_id=user.id,
                    problem_id=int(pid),
                    attempt_label=label,
                ).first()
                if exists:
                    continue
                row = Attempt(
                    user_id=user.id,
                    problem_id=int(pid),
                    attempt_label=label,
                    time_spent=(note.get("time_spent") or "").strip(),
                    approach=(note.get("approach") or "").strip(),
                    reflection=(note.get("reflection") or "").strip(),
                    solved=bool(note.get("solved")),
                )
                ts = note.get("timestamp")
                if ts:
                    try:
                        row.created_at = datetime.strptime(
                            str(ts).strip(), "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        pass
                db.session.add(row)
                n += 1
        db.session.commit()
        print(f"Imported {n} attempt row(s) for {username!r}.")


if __name__ == "__main__":
    main()
