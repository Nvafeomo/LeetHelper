# LeetTracker

Flask app for tracking LeetCode practice: browse a `leetcode.json` catalog, log attempts (time, approach, solved, notes), and view simple stats. An older CLI in `main.py` uses `data/problems.json` separately.

## Setup

```bash
pip install -r requirements.txt
```

Put `leetcode.json` at the project root (LeetCode `stat_status_pairs` style export).

## Run

**Web app:** `python app.py` → open http://127.0.0.1:5000

**CLI:** `python main.py`

## Usage

The web UI loads all problems from `leetcode.json` with title and difficulty. Sort by number, title, or difficulty; filter by title; paginate. Open a problem to log attempts and search past attempts by a keyword in your approach notes.

Stats include fastest hard solves (with problem number), average time by topic when you have topics, and per-problem time summaries.

### Optional topic tags

The default export has no tags. For topic filtering and richer category stats, add `data/problem_topics.json`: a JSON object mapping each problem’s slug to a list of tag strings:

```json
{
  "two-sum": ["Array", "Hash Table"],
  "number-of-islands": ["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"]
}
```

Slugs must match `question__title_slug` in the catalog. Use `{}` until you add entries.

## Project layout

```
LeetTracker/
├── leetcode.json
├── app.py
├── main.py
├── problem_tracker.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── utils/
│   ├── catalog.py
│   ├── storage.py
│   └── time_parse.py
└── data/
    ├── attempts.json
    ├── problem_topics.json
    └── problems.json    # CLI only
```

## Attempt records

Each attempt stores: auto-incremented `attempt`, `time_spent` (e.g. `"30 minutes"`), `approach`, `solved`, optional `reflection`, and `timestamp` when saved.

## Notes

Built for staying on track with LeetCode and practicing Python; the web UI is easier to show than the CLI alone. Possible next steps: pull time/metadata from LeetCode via extension or API, charts, spaced repetition, CSV/Markdown export, UI polish.
