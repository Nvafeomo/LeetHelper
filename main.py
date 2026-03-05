from problem_tracker import Problem
from utils.storage import (
    load_problems, save_problems, add_note_to_problem, 
    search_by_approach, fastest_hard_problems, most_time_consuming_categories,
    remove_problem, delete_note_from_problem
)
from datetime import datetime

DATA_FILE = "data/problems.json"
def safe_input(prompt):
    user_input = input(prompt)
    if user_input.strip().lower() in ["exit", "cancel", "x"]:
        print(" Exiting entry. Returning to menu.")
        return None
    return user_input

def add_problem():
    title = safe_input("Title: ")
    if title is None: return

    category = safe_input("Category: ")
    if category is None: return

    difficulty = safe_input("Difficulty (Easy/Medium/Hard): ")
    if difficulty is None: return

    status = safe_input("Status (Solved/Unsolved): ")
    if status is None: return

    link = safe_input("LeetCode Link: ")
    if link is None: return

    print("\n--- Reflection Notes ---")
    attempt = safe_input("Attempt number: ")
    if attempt is None: return

    approach = safe_input("Approach used: ")
    if approach is None: return

    reflection = safe_input("Reflection notes: ")
    if reflection is None: return

    time_spent = safe_input("Time spent (e.g. 30 minutes): ")
    if time_spent is None: return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    notes = [{
        "attempt": attempt,
        "approach": approach,
        "reflection": reflection,
        "time_spent": time_spent,
        "timestamp": timestamp
    }]

    new_problem = Problem(title, category, difficulty, status, link, notes)
    problems = load_problems(DATA_FILE)
    problems.append(new_problem.to_dict())
    save_problems(problems, DATA_FILE)
    print("✅ Problem added!")


def append_note():
    title = safe_input("Problem title to append note to: ")
    if title is None: return

    attempt = safe_input("Attempt number: ")
    if attempt is None: return

    approach = safe_input("Approach used: ")
    if approach is None: return

    reflection = safe_input("Reflection notes: ")
    if reflection is None: return

    time_spent = safe_input("Time spent (e.g. 30 minutes): ")
    if time_spent is None: return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = {
        "attempt": attempt,
        "approach": approach,
        "reflection": reflection,
        "time_spent": time_spent,
        "timestamp": timestamp
    }

    add_note_to_problem(title, note, DATA_FILE)


def search_approach():
    keyword = input("Approach keyword to search (e.g. greedy, DP): ")
    results = search_by_approach(keyword, DATA_FILE)
    if results:
        print(f"Found {len(results)} problem(s):")
        for r in results:
            print(f"- {r['title']} ({r['difficulty']})")
    else:
        print("No matching problems found.")

def view_time_stats():
    title = input("Enter problem title: ")
    problems = load_problems(DATA_FILE)
    for pdata in problems:
        if pdata["title"].lower() == title.lower():
            p = Problem(
                pdata["title"], pdata["category"], pdata["difficulty"],
                pdata["status"], pdata["link"], pdata.get("notes", [])
            )
            stats = p.get_time_stats()
            print(f"\nTime Stats for '{p.title}':")
            print(f"Average: {stats['average']} min")
            print(f"Shortest: {stats['shortest']} min")
            print(f"Longest: {stats['longest']} min")
            return
    print("Problem not found.")

def show_fastest_hard():
    results = fastest_hard_problems(DATA_FILE)
    print("\n Fastest Solved Hard Problems:")
    for title, time in results:
        print(f"- {title} → {time} min")

def show_slowest_categories():
    results = most_time_consuming_categories(DATA_FILE)
    print("\n Most Time-Consuming Categories:")
    for cat, avg in results:
        print(f"- {cat}: {avg} min (avg)")
def delete_problem():
    title = safe_input("Enter the exact title of the problem to delete: ")
    if title is None: return
    confirm = safe_input(f"Are you sure you want to delete '{title}'? (y/n): ")

    if confirm is None or confirm.lower() != 'y':
        print("❎ Problem deletion canceled.")
        return
    remove_problem(title, DATA_FILE)
def delete_note():
    title = safe_input("Problem title: ")
    if title is None: return

    attempt = safe_input("Attempt number to delete: ")
    if attempt is None: return

    confirm = safe_input(f"Delete attempt {attempt} from '{title}'? (y/n): ")
    if confirm is None or confirm.lower() != 'y':
        print("❎ Note deletion canceled.")
        return

    delete_note_from_problem(title, attempt, DATA_FILE)
    print(f"✅ Note for attempt {attempt} deleted from '{title}'.")
if __name__ == "__main__":
    print("📊 Welcome to LeetHelper!")
    while True:
        print("\n1. Add new problem")
        print("2. Append reflection note")
        print("3. Search problems by approach")
        print("4. View time stats for a problem")
        print("5. Show fastest hard problems")
        print("6. Show slowest categories")
        print("7. Delete a problem")
        print("8. Delete a reflection note")
        print("9. Exit")

        choice = input("Choose: ")

        if choice == '1':
            add_problem()
        elif choice == '2':
            append_note()
        elif choice == '3':
            search_approach()
        elif choice == '4':
            view_time_stats()
        elif choice == '5':
            show_fastest_hard()
        elif choice == '6':
            show_slowest_categories()
        elif choice == '7':
            delete_problem()
        elif choice == '8':
            delete_note()
        elif choice == '9':
            print("👋 Exiting LeetHelper. See you next time!")
            break
        else:
            print("❌ Invalid choice. Please enter a number from 1 to 9.")
                
