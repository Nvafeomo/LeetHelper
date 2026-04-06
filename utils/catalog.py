"""Load and cache LeetCode problem catalog from leetcode.json (stat_status_pairs export)."""
import json
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CATALOG_PATH = os.path.join(_ROOT, "leetcode.json")
TOPICS_PATH = os.path.join(_ROOT, "data", "problem_topics.json")
BLIND_75_PATH = os.path.join(_ROOT, "data", "blind75.json")

_cache_rows = None
_cache_key = None
_topics_cache = None
_topics_mtime = None
_blind_75_ids_cache = None
_blind_75_mtime = None


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


def _load_blind_75_ids():
    """Cached set of problem ids from data/blind75.json (mtime-based invalidation)."""
    global _blind_75_ids_cache, _blind_75_mtime
    if not os.path.isfile(BLIND_75_PATH):
        return frozenset()
    mtime = os.path.getmtime(BLIND_75_PATH)
    if _blind_75_ids_cache is not None and _blind_75_mtime == mtime:
        return _blind_75_ids_cache
    try:
        with open(BLIND_75_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        _blind_75_ids_cache = frozenset()
        _blind_75_mtime = mtime
        return _blind_75_ids_cache
    ids = []
    if isinstance(data, list):
        for x in data:
            try:
                ids.append(int(x))
            except (TypeError, ValueError):
                pass
    _blind_75_ids_cache = frozenset(ids)
    _blind_75_mtime = mtime
    return _blind_75_ids_cache


def normalize_list_key(raw):
    """Return 'all' or a known list id (e.g. 'blind75'); unknown values -> 'all'."""
    if not raw:
        return "all"
    key = str(raw).strip().lower()
    if key in ("", "all"):
        return "all"
    if key == "blind75":
        return "blind75"
    return "all"


def rows_for_catalog_list(rows, list_key):
    """Restrict rows to a curated id list. list_key 'all' means no restriction."""
    if not list_key or list_key == "all":
        return list(rows)
    if list_key == "blind75":
        allowed = _load_blind_75_ids()
        return [r for r in rows if r.get("id") in allowed]
    return list(rows)


def list_metadata(list_key, rows_after_list_filter):
    """
    Extra fields for API responses when using a named list.
    list_size: number of ids declared in the list file.
    matched_in_catalog: how many of those appear in the current leetcode.json export.
    """
    if list_key == "all":
        return {}
    if list_key == "blind75":
        declared = len(_load_blind_75_ids())
        matched = len(rows_after_list_filter)
        return {
            "list": "blind75",
            "list_size": declared,
            "matched_in_catalog": matched,
        }
    return {}


def load_catalog_rows(catalog_path=None, force_reload=False):
    """Return normalized list of problem dicts. Cached by catalog + topics mtimes."""
    global _cache_rows, _cache_key
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
