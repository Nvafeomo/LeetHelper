import json
from utils.time_parse import parse_time
from collections import defaultdict
# utils/storage.py
import os
import json

DATA_FILE = 'data/problems.json'

# Setup block
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.isfile(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Your save_problems() and load_problems() functions follow here...

def load_problems(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_problems(problems, filepath):
    with open(filepath, 'w') as file:
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

def search_by_approach(approach_keyword, filepath):
    problems = load_problems(filepath)
    matched = []
    for p in problems:
        for note in p.get("notes", []):
            if approach_keyword.lower() in note["approach"].lower():
                matched.append(p)
                break
    return matched

def fastest_hard_problems(filepath, top_n=5):
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

def most_time_consuming_categories(filepath):
    problems = load_problems(filepath)
    category_times = defaultdict(list)
    for p in problems:
        for note in p.get("notes", []):
            t = parse_time(note.get("time_spent", ""))
            if t is not None:
                category_times[p["category"]].append(t)
    averages = {
        cat: round(sum(times)/len(times), 2)
        for cat, times in category_times.items() if times
    }
    return sorted(averages.items(), key=lambda x: x[1], reverse=True)
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
