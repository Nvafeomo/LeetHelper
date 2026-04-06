import json
import os
from collections import defaultdict
from datetime import datetime

from utils.time_parse import parse_time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ATTEMPTS_FILE = os.path.join(_ROOT, "data", "attempts.json")

os.makedirs(os.path.dirname(ATTEMPTS_FILE), exist_ok=True)
if not os.path.isfile(ATTEMPTS_FILE):
    with open(ATTEMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_attempts(filepath=None):
    path = filepath or ATTEMPTS_FILE
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_attempts(data, filepath=None):
    path = filepath or ATTEMPTS_FILE
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_attempts_for_problem(problem_id, filepath=None):
    key = str(problem_id)
    all_a = load_attempts(filepath)
    entry = all_a.get(key) or {}
    return list(entry.get("attempts") or [])


def append_attempt(problem_id, note, filepath=None):
    """note: time_spent, approach, reflection, solved; attempt and timestamp set if missing."""
    key = str(problem_id)
    all_a = load_attempts(filepath)
    bucket = all_a.setdefault(key, {"attempts": []})
    attempts = bucket["attempts"]
    next_n = 1
    if attempts:
        try:
            next_n = max(int(str(x.get("attempt", 0))) for x in attempts) + 1
        except (TypeError, ValueError):
            next_n = len(attempts) + 1
    note = dict(note)
    note.setdefault("attempt", str(next_n))
    if not note.get("timestamp"):
        note["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attempts.append(note)
    save_attempts(all_a, filepath)
    return note


def delete_attempt(problem_id, attempt_num, filepath=None):
    key = str(problem_id)
    all_a = load_attempts(filepath)
    if key not in all_a:
        return False
    attempts = all_a[key].get("attempts") or []
    filtered = [n for n in attempts if str(n.get("attempt")) != str(attempt_num)]
    if len(filtered) == len(attempts):
        return False
    all_a[key]["attempts"] = filtered
    if not filtered:
        del all_a[key]
    save_attempts(all_a, filepath)
    return True


def search_attempts_by_approach(keyword, catalog_by_id, filepath=None):
    """Return list of problem summaries with attempt notes matching approach keyword."""
    if not keyword:
        return []
    kw = keyword.lower()
    all_a = load_attempts(filepath)
    out = []
    for pid, entry in all_a.items():
        meta = catalog_by_id.get(pid)
        if not meta:
            continue
        matched = []
        for n in entry.get("attempts") or []:
            if kw in (n.get("approach") or "").lower():
                matched.append(n)
        if matched:
            out.append(
                {
                    "id": meta["id"],
                    "title": meta["title"],
                    "difficulty": meta["difficulty"],
                    "tags": meta.get("tags") or [],
                    "notes": matched,
                }
            )
    return out


def _parse_attempt_timestamp(s):
    if not s:
        return datetime.min
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.min


def list_attempts_filtered(
    catalog_by_id, title_q="", topic_q="", approach_q="", filepath=None
):
    """
    Flat list of attempts with problem metadata. Filters are substring matches (case-insensitive).
    Empty filter means no filter for that dimension.
    Sorted by attempt timestamp descending (newest first).
    """
    title_q = (title_q or "").strip().lower()
    topic_q = (topic_q or "").strip().lower()
    approach_q = (approach_q or "").strip().lower()
    all_a = load_attempts(filepath)
    rows = []
    for pid, entry in all_a.items():
        meta = catalog_by_id.get(pid)
        if not meta:
            continue
        if title_q and title_q not in (meta.get("title") or "").lower():
            continue
        tags = meta.get("tags") or []
        if topic_q:
            if not any(topic_q in (t or "").lower() for t in tags):
                continue
        for n in entry.get("attempts") or []:
            ap = (n.get("approach") or "").lower()
            ref = (n.get("reflection") or "").lower()
            if approach_q and approach_q not in ap and approach_q not in ref:
                continue
            rows.append(
                {
                    "problem_id": meta["id"],
                    "title": meta["title"],
                    "difficulty": meta["difficulty"],
                    "tags": tags,
                    "attempt": n,
                }
            )
    rows.sort(
        key=lambda r: _parse_attempt_timestamp((r.get("attempt") or {}).get("timestamp")),
        reverse=True,
    )
    return rows


# --- Legacy CLI: data/problems.json (list of free-form problems) ---

PROBLEMS_LEGACY_FILE = os.path.join(_ROOT, "data", "problems.json")
if not os.path.isfile(PROBLEMS_LEGACY_FILE):
    os.makedirs(os.path.dirname(PROBLEMS_LEGACY_FILE), exist_ok=True)
    with open(PROBLEMS_LEGACY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_problems(filepath):
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_problems(problems, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(problems, file, indent=4)


def add_note_to_problem(title, new_note, filepath):
    problems = load_problems(filepath)
    for p in problems:
        if p["title"].lower() == title.lower():
            p.setdefault("notes", []).append(new_note)
            save_problems(problems, filepath)
            print("Note added successfully.")
            return True
    print(f"No problem found with title: {title}")
    return False


def search_by_approach(keyword, filepath):
    problems = load_problems(filepath)
    matched = []
    for p in problems:
        for note in p.get("notes", []):
            if keyword.lower() in (note.get("approach") or "").lower():
                matched.append(p)
                break
    return matched


def remove_problem(title, filepath):
    problems = load_problems(filepath)
    filtered = [p for p in problems if p["title"].lower() != title.lower()]
    if len(filtered) == len(problems):
        print("Problem not found.")
        return False
    save_problems(filtered, filepath)
    print(f"✅ Problem '{title}' removed.")
    return True


def delete_note_from_problem(title, attempt_num, filepath):
    problems = load_problems(filepath)
    for p in problems:
        if p["title"].lower() == title.lower():
            notes = p.get("notes", [])
            filtered = [n for n in notes if str(n.get("attempt")) != str(attempt_num)]
            if len(filtered) == len(notes):
                print("Note not found.")
                return False
            p["notes"] = filtered
            save_problems(problems, filepath)
            print(f" Removed note for attempt {attempt_num}.")
            return True
    print("Problem not found.")
    return False


def _time_stats_from_notes(notes):
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


def time_stats_for_problem(problem_id, filepath=None):
    notes = get_attempts_for_problem(problem_id, filepath)
    return _time_stats_from_notes(notes)


def catalog_fastest_by_difficulty(catalog_by_id, difficulty, filepath=None, top_n=5):
    """List of (title, problem_id, minutes) for fastest first timed attempt at given difficulty."""
    diff_lower = (difficulty or "").strip().lower()
    if diff_lower not in ("easy", "medium", "hard"):
        return []
    all_a = load_attempts(filepath)
    rows = []
    for pid, entry in all_a.items():
        meta = catalog_by_id.get(pid)
        if not meta or meta.get("difficulty", "").lower() != diff_lower:
            continue
        for note in entry.get("attempts") or []:
            time_minutes = parse_time(note.get("time_spent", ""))
            if time_minutes is not None:
                rows.append((meta["title"], int(pid), time_minutes))
                break
    rows.sort(key=lambda x: x[2])
    return [(t, pid, m) for t, pid, m in rows[:top_n]]


def catalog_fastest_hard_problems(catalog_by_id, filepath=None, top_n=5):
    """List of (title, problem_id, minutes) for fastest first timed hard attempt."""
    return catalog_fastest_by_difficulty(catalog_by_id, "hard", filepath, top_n)


def catalog_slowest_tags(catalog_by_id, filepath=None):
    """Average time per first tag (or 'Uncategorized')."""
    all_a = load_attempts(filepath)
    category_times = defaultdict(list)
    for pid, entry in all_a.items():
        meta = catalog_by_id.get(pid)
        if not meta:
            continue
        tags = meta.get("tags") or []
        cat = tags[0] if tags else "Uncategorized"
        for note in entry.get("attempts") or []:
            t = parse_time(note.get("time_spent", ""))
            if t is not None:
                category_times[cat].append(t)
    averages = {
        cat: round(sum(times) / len(times), 2)
        for cat, times in category_times.items()
        if times
    }
    return sorted(averages.items(), key=lambda x: x[1], reverse=True)


def fastest_hard_problems_legacy(filepath, top_n=5):
    """CLI: problems.json list format; returns list of (title, minutes)."""
    problems = load_problems(filepath)
    hard_problems = []
    for p in problems:
        if p["difficulty"].lower() != "hard":
            continue
        for note in p.get("notes", []):
            time_minutes = parse_time(note.get("time_spent", ""))
            if time_minutes is not None:
                hard_problems.append((p["title"], time_minutes))
                break
    return sorted(hard_problems, key=lambda x: x[1])[:top_n]


def most_time_consuming_categories_legacy(filepath):
    """CLI: problems.json; category field on each problem."""
    problems = load_problems(filepath)
    category_times = defaultdict(list)
    for p in problems:
        for note in p.get("notes", []):
            t = parse_time(note.get("time_spent", ""))
            if t is not None:
                category_times[p["category"]].append(t)
    averages = {
        cat: round(sum(times) / len(times), 2)
        for cat, times in category_times.items()
        if times
    }
    return sorted(averages.items(), key=lambda x: x[1], reverse=True)
