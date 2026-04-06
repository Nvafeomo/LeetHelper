"""Flask web app for LeetTracker (catalog + attempts)."""
import os

from flask import Flask, render_template, request, jsonify

from utils.catalog import (
    load_catalog_rows,
    catalog_by_id,
    filter_sort_page,
    iter_unique_tags,
    list_metadata,
    normalize_list_key,
    rows_for_catalog_list,
)
from utils.storage import (
    append_attempt,
    delete_attempt,
    get_attempts_for_problem,
    list_attempts_filtered,
    search_attempts_by_approach,
    time_stats_for_problem,
    catalog_fastest_by_difficulty,
    catalog_fastest_hard_problems,
    catalog_slowest_tags,
)

app = Flask(__name__)


def _get_catalog_map():
    rows = load_catalog_rows()
    return catalog_by_id()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/catalog", methods=["GET"])
def api_catalog():
    """
    Query params:
      list   — optional; 'all' (default) or 'blind75'. Restricts rows to ids in data/blind75.json.
      q      — title substring filter.
      tag    — topic tag (from problem_topics.json).
      sort   — id | title | difficulty
      order  — asc | desc
      limit, offset — pagination

    Response always includes items, total, limit, offset.
    When list=blind75, also includes list, list_size (ids in file), matched_in_catalog (present in export).
    """
    list_key = normalize_list_key(request.args.get("list", "all"))
    rows = load_catalog_rows()
    rows = rows_for_catalog_list(rows, list_key)
    extra = list_metadata(list_key, rows)

    q = request.args.get("q", "")
    tag = request.args.get("tag", "")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        limit = 100
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0
    page, total = filter_sort_page(
        rows, q=q, tag=tag, sort_by=sort_by, order=order, limit=limit, offset=offset
    )
    payload = {"items": page, "total": total, "limit": limit, "offset": offset}
    payload.update(extra)
    return jsonify(payload)


@app.route("/api/catalog/tags", methods=["GET"])
def api_catalog_tags():
    """Same `list` param as GET /api/catalog — tags are computed only from rows in that list."""
    list_key = normalize_list_key(request.args.get("list", "all"))
    rows = load_catalog_rows()
    rows = rows_for_catalog_list(rows, list_key)
    return jsonify(iter_unique_tags(rows))


@app.route("/api/catalog/<int:problem_id>", methods=["GET"])
def api_catalog_one(problem_id):
    cmap = _get_catalog_map()
    key = str(problem_id)
    meta = cmap.get(key)
    if not meta:
        return jsonify({"error": "Problem not found"}), 404
    attempts = get_attempts_for_problem(problem_id)
    return jsonify({**meta, "attempts": attempts})


@app.route("/api/catalog/<int:problem_id>/attempts", methods=["POST"])
def api_add_attempt(problem_id):
    cmap = _get_catalog_map()
    if str(problem_id) not in cmap:
        return jsonify({"error": "Problem not found"}), 404
    data = request.get_json() or {}
    time_spent = (data.get("time_spent") or "").strip()
    approach = (data.get("approach") or "").strip()
    if not time_spent or not approach:
        return jsonify({"error": "time_spent and approach are required"}), 400
    reflection = (data.get("reflection") or "").strip()
    solved = bool(data.get("solved"))
    note = {
        "time_spent": time_spent,
        "approach": approach,
        "reflection": reflection,
        "solved": solved,
    }
    saved = append_attempt(problem_id, note)
    return jsonify({"success": True, "attempt": saved})


@app.route("/api/catalog/<int:problem_id>/attempts/<attempt>", methods=["DELETE"])
def api_delete_attempt(problem_id, attempt):
    ok = delete_attempt(problem_id, attempt)
    if not ok:
        return jsonify({"error": "Attempt not found"}), 404
    return jsonify({"success": True})


@app.route("/api/attempts", methods=["GET"])
def api_list_attempts():
    """
    Flat list of attempts with problem metadata. Query params (all optional, substring match):
      title    — problem title
      topic    — any topic tag
      approach — approach or reflection text
    """
    title = request.args.get("title", "")
    topic = request.args.get("topic", "")
    approach = request.args.get("approach", "")
    cmap = _get_catalog_map()
    rows = list_attempts_filtered(
        cmap, title_q=title, topic_q=topic, approach_q=approach
    )
    return jsonify(rows)


@app.route("/api/search", methods=["GET"])
def api_search():
    """Legacy: grouped by problem; approach keyword only. Prefer GET /api/attempts."""
    keyword = request.args.get("q", "")
    cmap = _get_catalog_map()
    results = search_attempts_by_approach(keyword, cmap)
    return jsonify(results)


@app.route("/api/stats/time/<int:problem_id>")
def api_time_stats(problem_id):
    cmap = _get_catalog_map()
    if str(problem_id) not in cmap:
        return jsonify({"error": "Problem not found"}), 404
    stats = time_stats_for_problem(problem_id)
    return jsonify(stats)


def _fastest_json(rows):
    return jsonify([{"title": t, "id": pid, "minutes": m} for t, pid, m in rows])


@app.route("/api/stats/fastest-hard")
def api_fastest_hard():
    cmap = _get_catalog_map()
    return _fastest_json(catalog_fastest_hard_problems(cmap))


@app.route("/api/stats/fastest")
def api_fastest_by_query():
    """GET /api/stats/fastest?difficulty=easy|medium|hard — fastest first timed attempt per difficulty."""
    d = (request.args.get("difficulty") or "").strip().lower()
    if d not in ("easy", "medium", "hard"):
        return jsonify({"error": "difficulty must be easy, medium, or hard"}), 400
    cmap = _get_catalog_map()
    return _fastest_json(catalog_fastest_by_difficulty(cmap, d))


@app.route("/api/stats/slowest-categories")
def api_slowest_categories():
    cmap = _get_catalog_map()
    results = catalog_slowest_tags(cmap)
    return jsonify([{"category": c, "avg_minutes": a} for c, a in results])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
