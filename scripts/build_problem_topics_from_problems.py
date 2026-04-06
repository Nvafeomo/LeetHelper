"""
Build data/problem_topics.json from problems/*.json (LeetCode problem dumps).

Skips non–interview-style tracks:
  - SQL: topics are exactly ["Database"] (94 problems in typical dumps)
  - Shell: topics are exactly ["Shell"] (4 problems)

Omits problems with empty topics (nothing to show in the UI).

Usage (from repo root): python scripts/build_problem_topics_from_problems.py
"""
import json
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROBLEMS_DIR = os.path.join(_ROOT, "problems")
OUT_PATH = os.path.join(_ROOT, "data", "problem_topics.json")

# Topic sets that mean "not the usual DSA interview problem" for this dataset.
_SKIP_TOPIC_SETS = frozenset(
    {
        frozenset({"Database"}),
        frozenset({"Shell"}),
    }
)


def _should_skip(topics):
    if not topics:
        return True
    s = frozenset(topics)
    return s in _SKIP_TOPIC_SETS


def main():
    out = {}
    skipped_sql = 0
    skipped_shell = 0
    skipped_empty = 0
    for fn in os.listdir(PROBLEMS_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(PROBLEMS_DIR, fn)
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        slug = (d.get("problem_slug") or "").strip()
        if not slug:
            continue
        topics = d.get("topics") or []
        if not topics:
            skipped_empty += 1
            continue
        if _should_skip(topics):
            if frozenset(topics) == frozenset({"Database"}):
                skipped_sql += 1
            elif frozenset(topics) == frozenset({"Shell"}):
                skipped_shell += 1
            continue
        # Preserve order from source; normalize to list of strings
        out[slug] = [str(t) for t in topics]

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    print(f"Wrote {len(out)} slugs to {OUT_PATH}")
    print(f"Skipped empty topics: {skipped_empty}")
    print(f"Skipped SQL (Database only): {skipped_sql}")
    print(f"Skipped Shell only: {skipped_shell}")


if __name__ == "__main__":
    main()
