"""Flask web app for LeetTracker."""
import os
from flask import Flask, render_template, request, jsonify
from problem_tracker import Problem
from utils.storage import (
    load_problems, save_problems, add_note_to_problem,
    search_by_approach, fastest_hard_problems, most_time_consuming_categories,
    remove_problem, delete_note_from_problem
)
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "problems.json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/problems", methods=["GET"])
def get_problems():
    problems = load_problems(DATA_FILE)
    return jsonify(problems)


@app.route("/api/problems", methods=["POST"])
def create_problem():
    data = request.get_json()
    required = ["title", "category", "difficulty", "status", "link", "attempt", "approach", "reflection", "time_spent"]
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notes = [{
        "attempt": str(data["attempt"]),
        "approach": data["approach"],
        "reflection": data["reflection"],
        "time_spent": data["time_spent"],
        "timestamp": timestamp
    }]
    problem = Problem(
        data["title"], data["category"], data["difficulty"],
        data["status"], data["link"], notes
    )
    problems = load_problems(DATA_FILE)
    problems.append(problem.to_dict())
    save_problems(problems, DATA_FILE)
    return jsonify({"success": True, "message": "Problem added!"})


@app.route("/api/problems/<title>/notes", methods=["POST"])
def append_note(title):
    data = request.get_json()
    required = ["attempt", "approach", "reflection", "time_spent"]
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note = {
        "attempt": str(data["attempt"]),
        "approach": data["approach"],
        "reflection": data["reflection"],
        "time_spent": data["time_spent"],
        "timestamp": timestamp
    }
    success = add_note_to_problem(title, note, DATA_FILE)
    if not success:
        return jsonify({"error": "Problem not found"}), 404
    return jsonify({"success": True, "message": "Note added!"})


@app.route("/api/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "")
    if not keyword:
        return jsonify([])
    results = search_by_approach(keyword, DATA_FILE)
    return jsonify(results)


@app.route("/api/stats/time/<title>")
def time_stats(title):
    problems = load_problems(DATA_FILE)
    for pdata in problems:
        if pdata["title"].lower() == title.lower():
            p = Problem(
                pdata["title"], pdata["category"], pdata["difficulty"],
                pdata["status"], pdata["link"], pdata.get("notes", [])
            )
            stats = p.get_time_stats()
            return jsonify(stats)
    return jsonify({"error": "Problem not found"}), 404


@app.route("/api/stats/fastest-hard")
def fastest_hard():
    results = fastest_hard_problems(DATA_FILE)
    return jsonify([{"title": t, "minutes": m} for t, m in results])


@app.route("/api/stats/slowest-categories")
def slowest_categories():
    results = most_time_consuming_categories(DATA_FILE)
    return jsonify([{"category": c, "avg_minutes": a} for c, a in results])


@app.route("/api/problems/<title>", methods=["DELETE"])
def delete_problem(title):
    success = remove_problem(title, DATA_FILE)
    if not success:
        return jsonify({"error": "Problem not found"}), 404
    return jsonify({"success": True, "message": "Problem removed"})


@app.route("/api/problems/<title>/notes/<attempt>", methods=["DELETE"])
def delete_note(title, attempt):
    success = delete_note_from_problem(title, attempt, DATA_FILE)
    if not success:
        return jsonify({"error": "Problem or note not found"}), 404
    return jsonify({"success": True, "message": "Note removed"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
