# LeetTracker

A Python project for tracking LeetCode practice: a **Flask web app** that browses a full problem catalog and logs attempts, plus an optional **CLI** that still uses free-form `data/problems.json`.

**Tutorial PDF:** see [`docs/leettracker-guide.tex`](docs/leettracker-guide.tex) (step-by-step Flask + frontend guide with diagrams). Build instructions: [`docs/README.md`](docs/README.md).

---

## Features (web app)

- Browse **all problems** from [`leetcode.json`](leetcode.json) (LeetCode `stat_status_pairs` export) with **title** and **difficulty** shown from the file (no manual typing).
- **Sort** by problem number, title, or difficulty; **filter** by title substring; **paginate** the list.
- Click a problem to **log attempts**: time spent, approach, solved or not, optional reflection.
- **Search attempts** by approach keyword across your logged attempts.
- **Stats**: fastest hard problems (with problem #), average time by topic (first tag when topics exist), time stats per problem #.

### Topic tags (Array, Graph, …)

The bundled `leetcode.json` export does **not** include per-problem topic tags. To enable **topic filtering** and richer **“slowest category”** stats, add [`data/problem_topics.json`](data/problem_topics.json): a JSON object mapping **slug** to a list of tag strings, for example:

```json
{
  "two-sum": ["Array", "Hash Table"],
  "number-of-islands": ["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"]
}
```

Slugs must match `question__title_slug` in the catalog. An empty `{}` is valid until you fill it in.

---

## Folder structure

```text
LeetTracker/
├── docs/
│   ├── leettracker-guide.tex   # LaTeX tutorial (build PDF locally)
│   └── README.md               # how to compile the guide
├── leetcode.json          # Full catalog export (project root)
├── main.py                # CLI (legacy problems.json)
├── app.py                 # Flask web app
├── problem_tracker.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── utils/
│   ├── catalog.py       # Catalog load/cache, filters
│   ├── storage.py       # Attempts + legacy CLI storage
│   └── time_parse.py
├── data/
│   ├── attempts.json    # Your attempts (keyed by LeetCode frontend problem #)
│   ├── problem_topics.json
│   └── problems.json    # Legacy CLI only
```

---

## How to run

### Web app

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `leetcode.json` is present at the project root (your export).
3. Run: `python app.py`
4. Open http://127.0.0.1:5000

### CLI (legacy)

1. `python main.py`
2. Uses `data/problems.json` for manually entered problems (separate from the web catalog).

---

## Attempt fields

Each attempt stores:

- `attempt` — auto-incremented
- `time_spent` — e.g. `"30 minutes"`
- `approach` — short description
- `solved` — boolean
- `reflection` — optional
- `timestamp` — set when the attempt is saved

---

## Why I built this

To keep track of LeetCode progress and stay accountable. I originally built the CLI to help monitor LeetCode progress and brush up my Python skills; I added a Flask + HTML/CSS frontend so the project is easier to show on a resume.

You can **view time stats** per problem, **search by approach keyword**, **see fastest-solved hard problems**, and **find slowest categories by average time**—useful for competitive prep, spaced repetition, and reflection.

---

## Future ideas

- Use a browser extension or API to collect time spent and problem info from LeetCode.
- Visualize performance with `matplotlib`.
- Add spaced repetition or revisit tracking.
- Export to CSV or Markdown for publishing.
- Polish the web UI and make more of the prompts optional.
