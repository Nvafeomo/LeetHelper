"""Per-user attempt storage backed by SQLAlchemy."""
from collections import defaultdict
from datetime import datetime

from extensions import db
from models import Attempt
from utils.time_parse import parse_time


def _next_attempt_label(user_id: int, problem_id: int) -> str:
    rows = (
        Attempt.query.filter_by(user_id=user_id, problem_id=problem_id)
        .with_entities(Attempt.attempt_label)
        .all()
    )
    labels = [r[0] for r in rows]
    best = 0
    for lab in labels:
        try:
            best = max(best, int(str(lab)))
        except (TypeError, ValueError):
            continue
    return str(best + 1)


def get_attempts_for_problem(problem_id, user_id: int):
    rows = (
        Attempt.query.filter_by(user_id=user_id, problem_id=int(problem_id))
        .order_by(Attempt.id.asc())
        .all()
    )
    return [r.to_note_dict() for r in rows]


def append_attempt(problem_id, note, user_id: int):
    """note: time_spent, approach, reflection, solved; attempt and timestamp set if missing."""
    pid = int(problem_id)
    note = dict(note)
    if not note.get("attempt"):
        note["attempt"] = _next_attempt_label(user_id, pid)
    ts = note.get("timestamp")
    row = Attempt(
        user_id=user_id,
        problem_id=pid,
        attempt_label=str(note["attempt"]),
        time_spent=(note.get("time_spent") or "").strip(),
        approach=(note.get("approach") or "").strip(),
        reflection=(note.get("reflection") or "").strip(),
        solved=bool(note.get("solved")),
    )
    if ts:
        try:
            row.created_at = datetime.strptime(str(ts).strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    db.session.add(row)
    db.session.commit()
    return row.to_note_dict()


def delete_attempt(problem_id, attempt_num, user_id: int):
    row = Attempt.query.filter_by(
        user_id=user_id,
        problem_id=int(problem_id),
        attempt_label=str(attempt_num),
    ).first()
    if not row:
        return False
    db.session.delete(row)
    db.session.commit()
    return True


def search_attempts_by_approach(keyword, catalog_by_id, user_id: int):
    if not keyword:
        return []
    kw = keyword.lower()
    rows = Attempt.query.filter_by(user_id=user_id).all()
    by_problem = defaultdict(list)
    for r in rows:
        ap = (r.approach or "").lower()
        if kw in ap:
            by_problem[r.problem_id].append(r.to_note_dict())
    out = []
    for pid, notes in by_problem.items():
        meta = catalog_by_id.get(str(pid))
        if not meta:
            continue
        out.append(
            {
                "id": meta["id"],
                "title": meta["title"],
                "difficulty": meta["difficulty"],
                "tags": meta.get("tags") or [],
                "notes": notes,
            }
        )
    return out


def _parse_attempt_timestamp(s):
    from datetime import datetime

    if not s:
        return datetime.min
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.min


def list_attempts_filtered(
    catalog_by_id, user_id: int, title_q="", topic_q="", approach_q=""
):
    title_q = (title_q or "").strip().lower()
    topic_q = (topic_q or "").strip().lower()
    approach_q = (approach_q or "").strip().lower()
    rows = Attempt.query.filter_by(user_id=user_id).all()
    flat = []
    for r in rows:
        pid = str(r.problem_id)
        meta = catalog_by_id.get(pid)
        if not meta:
            continue
        if title_q and title_q not in (meta.get("title") or "").lower():
            continue
        tags = meta.get("tags") or []
        if topic_q:
            if not any(topic_q in (t or "").lower() for t in tags):
                continue
        ap = (r.approach or "").lower()
        ref = (r.reflection or "").lower()
        if approach_q and approach_q not in ap and approach_q not in ref:
            continue
        n = r.to_note_dict()
        flat.append(
            {
                "problem_id": meta["id"],
                "title": meta["title"],
                "difficulty": meta["difficulty"],
                "tags": tags,
                "attempt": n,
            }
        )
    flat.sort(
        key=lambda row: _parse_attempt_timestamp((row.get("attempt") or {}).get("timestamp")),
        reverse=True,
    )
    return flat


def time_stats_for_problem(problem_id, user_id: int):
    notes = get_attempts_for_problem(problem_id, user_id)
    times = []
    for note in notes:
        t = parse_time(note.get("time_spent", ""))
        if t is not None:
            times.append(t)
    if not times:
        return {"average": None, "shortest": None, "longest": None}
    avg = sum(times) / len(times)
    return {
        "average": round(avg, 2),
        "shortest": min(times),
        "longest": max(times),
    }


def catalog_fastest_by_difficulty(catalog_by_id, difficulty, user_id: int, top_n=5):
    diff_lower = (difficulty or "").strip().lower()
    if diff_lower not in ("easy", "medium", "hard"):
        return []
    rows = (
        Attempt.query.filter_by(user_id=user_id)
        .order_by(Attempt.problem_id, Attempt.created_at.asc(), Attempt.id.asc())
        .all()
    )
    seen = {}
    for r in rows:
        pid = str(r.problem_id)
        meta = catalog_by_id.get(pid)
        if not meta or meta.get("difficulty", "").lower() != diff_lower:
            continue
        if pid in seen:
            continue
        time_minutes = parse_time(r.time_spent or "")
        if time_minutes is not None:
            seen[pid] = (meta["title"], int(pid), time_minutes)
    out = list(seen.values())
    out.sort(key=lambda x: x[2])
    return [(t, pid, m) for t, pid, m in out[:top_n]]


def catalog_fastest_hard_problems(catalog_by_id, user_id: int, top_n=5):
    return catalog_fastest_by_difficulty(catalog_by_id, "hard", user_id, top_n)


def catalog_slowest_tags(catalog_by_id, user_id: int):
    rows = (
        Attempt.query.filter_by(user_id=user_id)
        .order_by(Attempt.problem_id, Attempt.created_at.asc(), Attempt.id.asc())
        .all()
    )
    category_times = defaultdict(list)
    for r in rows:
        pid = str(r.problem_id)
        meta = catalog_by_id.get(pid)
        if not meta:
            continue
        tags = meta.get("tags") or []
        cat = tags[0] if tags else "Uncategorized"
        t = parse_time(r.time_spent or "")
        if t is not None:
            category_times[cat].append(t)
    averages = {
        cat: round(sum(times) / len(times), 2)
        for cat, times in category_times.items()
        if times
    }
    return sorted(averages.items(), key=lambda x: x[1], reverse=True)
