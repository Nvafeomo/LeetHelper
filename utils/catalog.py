"""Load and cache LeetCode problem catalog from leetcode.json (stat_status_pairs export)."""
import json
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CATALOG_PATH = os.path.join(_ROOT, "leetcode.json")
TOPICS_PATH = os.path.join(_ROOT, "data", "problem_topics.json")

_cache_rows = None
_cache_key = None
_cache_path = None
_topics_cache = None
_topics_mtime = None


def level_to_label(level):
    if level == 1:
        return "Easy"
    if level == 2:
        return "Medium"
    if level == 3:
        return "Hard"
    return "Unknown"


def _load_topic_tags():
    global _topics_cache, _topics_mtime
    if not os.path.isfile(TOPICS_PATH):
        return {}
    mtime = os.path.getmtime(TOPICS_PATH)
    if _topics_cache is not None and _topics_mtime == mtime:
        return _topics_cache
    try:
        with open(TOPICS_PATH, encoding="utf-8") as f:
            _topics_cache = json.load(f)
        _topics_mtime = mtime
    except (json.JSONDecodeError, OSError):
        _topics_cache = {}
    return _topics_cache if isinstance(_topics_cache, dict) else {}


def _topics_file_mtime():
    if not os.path.isfile(TOPICS_PATH):
        return None
    return os.path.getmtime(TOPICS_PATH)


def load_catalog_rows(catalog_path=None, force_reload=False):
    """Return normalized list of problem dicts. Cached by catalog + topics mtimes."""
    global _cache_rows, _cache_key, _cache_path
    path = catalog_path or DEFAULT_CATALOG_PATH
    if not os.path.isfile(path):
        return []
    mtime = os.path.getmtime(path)
    tkey = _topics_file_mtime()
    key = (path, mtime, tkey)
    if not force_reload and _cache_rows is not None and _cache_key == key:
        return _cache_rows

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    pairs = data.get("stat_status_pairs") or []
    topics = _load_topic_tags()

    rows = []
    for pair in pairs:
        stat = pair.get("stat") or {}
        diff = pair.get("difficulty") or {}
        level = diff.get("level")
        if level is None:
            level = 0
        slug = stat.get("question__title_slug") or ""
        fid = stat.get("frontend_question_id")
        if fid is None:
            continue
        tag_list = topics.get(slug)
        if tag_list is None:
            tag_list = []
        elif isinstance(tag_list, str):
            tag_list = [tag_list]
        else:
            tag_list = list(tag_list)
        rows.append(
            {
                "id": int(fid),
                "title": stat.get("question__title") or "",
                "slug": slug,
                "difficulty": level_to_label(level),
                "difficulty_level": int(level),
                "paid_only": bool(pair.get("paid_only")),
                "link": f"https://leetcode.com/problems/{slug}/" if slug else "",
                "tags": tag_list,
            }
        )

    _cache_rows = rows
    _cache_key = key
    _cache_path = path
    return rows


def catalog_by_id(catalog_path=None):
    """Map str(problem_id) -> normalized row."""
    rows = load_catalog_rows(catalog_path)
    return {str(r["id"]): r for r in rows}


def iter_unique_tags(rows):
    seen = set()
    for r in rows:
        for t in r.get("tags") or []:
            if t:
                seen.add(t)
    return sorted(seen, key=str.lower)


def filter_sort_page(rows, q="", tag="", sort_by="id", order="asc", limit=100, offset=0):
    """Filter by title substring and optional tag; sort; paginate."""
    items = list(rows)
    q = (q or "").strip().lower()
    if q:
        items = [r for r in items if q in (r.get("title") or "").lower()]
    tag = (tag or "").strip().lower()
    if tag:
        items = [
            r
            for r in items
            if any(tag in (t or "").lower() for t in (r.get("tags") or []))
        ]

    reverse = (order or "asc").lower() == "desc"
    sort_by = (sort_by or "id").lower()

    if sort_by == "title":
        items.sort(key=lambda r: (r.get("title") or "").lower(), reverse=reverse)
    elif sort_by == "difficulty":
        items.sort(
            key=lambda r: (r.get("difficulty_level") or 0, r.get("id") or 0),
            reverse=reverse,
        )
    else:
        items.sort(key=lambda r: r.get("id") or 0, reverse=reverse)

    total = len(items)
    limit = max(1, min(int(limit or 100), 500))
    offset = max(0, int(offset or 0))
    page = items[offset : offset + limit]
    return page, total
