# LeetTracker

**LeetTracker** is a small web app for tracking LeetCode practice: browse a problem catalog, log each attempt (time, approach, whether you solved it, notes), search what you’ve written before, and skim a few stats. There’s also a legacy CLI if you prefer a terminal workflow.

---

## Motivation

Interview prep on LeetCode is easy to start and hard to keep honest. I wanted a single place to see the full catalog, record how each solve went, and look back at patterns (topics, time, “what did I try last time?”) without juggling spreadsheets. The project doubles as a way to practice Python, Flask, and a bit of front-end work.

---

## Features

- **Catalog** — Load problems from a LeetCode-style `leetcode.json` export (titles, difficulty, links). Sort, filter by title, paginate.
- **Curated lists** — Dropdown to view **all problems** or **Blind 75** (`data/blind75.json`, classic LeetCode Blind 75 ids).
- **Attempts** — Per problem: time spent, approach, solved flag, optional reflection; timestamps and attempt numbers.
- **Search** — Find past attempts by a keyword in your approach notes.
- **Topic tags (optional)** — `data/problem_topics.json` maps problem slugs to tags so you can filter by topic and improve stats.
- **Stats** — Fastest hard solves, slowest topics (when tags exist), per-problem time summaries.
- **REST-style API** — JSON endpoints for catalog, attempts, search, and stats (used by the bundled UI).
- **CLI** — `main.py` + `data/problems.json` for a separate, manual problem list (older workflow).

---

## Architecture (high level)

- **Backend:** Flask serves one HTML shell (`templates/index.html`) and JSON routes under `/api/…`. Catalog logic lives in `utils/catalog.py` (load export, cache, filters, Blind 75 list). Attempts and legacy CLI data go through `utils/storage.py` and `utils/time_parse.py`.
- **Frontend:** Vanilla JavaScript (`static/app.js`) calls the API with `fetch`; styling in `static/style.css`. No React—keeps the stack small.
- **Data:** No database in the current version. Problem metadata comes from `leetcode.json`; your logged attempts live in **`data/attempts.json`**. Optional tags and Blind 75 ids are JSON files under `data/`.

**Flow:** Browser → Flask routes → read/write JSON + in-memory catalog cache → JSON responses → JS updates the table, modal, search, and stats.

---

## Project structure

```
LeetTracker/
├── app.py                 # Flask app + API routes
├── main.py                # CLI entry
├── problem_tracker.py     # CLI problem model
├── leetcode.json          # LeetCode catalog export (project root)
├── requirements.txt
├── templates/
│   └── index.html         # Single-page shell
├── static/
│   ├── app.js             # Catalog UI, modal, search, stats
│   └── style.css
├── utils/
│   ├── catalog.py         # Catalog load/cache, filters, Blind 75
│   ├── storage.py         # attempts.json + CLI storage
│   └── time_parse.py      # Parse time strings for stats
└── data/
    ├── attempts.json      # Your logged attempts (created if missing)
    ├── blind75.json       # Blind 75 problem ids
    ├── problem_topics.json   # Optional slug → [tags]
    └── problems.json      # CLI-only manual problems
```

---

## Setup

**Requirements:** Python 3.10+ recommended.

```bash
git clone <your-repo-url>
cd LeetTracker
pip install -r requirements.txt
```

Place **`leetcode.json`** at the project root (LeetCode `stat_status_pairs` style export). Keep **`data/blind75.json`** and optional **`data/problem_topics.json`** as needed.

**Environment variables:** None required for local dev. For production, set at least `SECRET_KEY` if you add sessions later; see deployment notes.

**Run locally**

```bash
python app.py
```

Open **http://127.0.0.1:5000** (Flask dev server).

**CLI**

```bash
python main.py
```

---

## Deployment (e.g. Railway)

The dev server is not meant for production. Use a WSGI server (e.g. **Gunicorn**) and bind to the host’s port:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Add `gunicorn` to `requirements.txt` on the branch you deploy. Platforms like **Railway** set `PORT` for you.

**Persistence:** `data/attempts.json` must live on **persistent disk** (e.g. a volume mounted at `data/`) if you don’t want attempts wiped on redeploy.

**Authentication:** The app does **not** ship with login yet. A public URL means **one shared `attempts.json`** for everyone unless you add accounts or client-only storage. Fine for a personal demo; use auth + per-user storage for multi-user production.

---

## Authentication

*Not implemented in the current codebase.* A typical next step would be Flask sessions or Flask-Login, password hashes in SQLite (or similar), and scoping every attempt read/write by `user_id`. Until then, treat deployment as **single-user / demo** or keep the app local.

---

## Data model (JSON, not SQL)

| Piece | Role |
|--------|------|
| `leetcode.json` | Full problem catalog from LeetCode export. |
| `data/attempts.json` | Map of problem id → `{ "attempts": [ ... ] }` with fields below. |
| `data/problem_topics.json` | `{ "problem-slug": ["Array", "Hash Table", ...] }` |
| `data/blind75.json` | Array of 75 frontend problem ids for the Blind 75 filter. |

**Each attempt** (roughly): `attempt`, `time_spent`, `approach`, `solved`, optional `reflection`, `timestamp`.

---

## Testing

There is no automated test suite in this repo yet. Running tests would be a good addition (e.g. pytest for `utils/catalog.py` and storage helpers).

---

## Screenshots

Add a few images or a GIF here when you’re ready—for example:

- **Catalog** — full list or Blind 75 filter  
- **Attempt modal** — logging time, approach, reflection  
- **Stats** — fastest hard, topic times, per-problem stats  

Example markdown (create a folder like `docs/screenshots/` and point paths at your files):

```markdown
![Catalog view](docs/screenshots/catalog.png)
![Logging an attempt](docs/screenshots/attempt.png)
```

A short GIF of browse → open problem → save attempt reads well on GitHub.

---

## Roadmap / ideas

- User accounts and per-user attempts (SQLite or Postgres).
- Charts (e.g. time over time, difficulty mix).
- Export to CSV or Markdown.
- Browser extension or script to pull metadata from LeetCode.
- Spaced repetition or “review queue.”
- Production hardening: CSRF for state-changing routes if cookies are added, rate limits on auth.

---

## Tech stack

| Area | Choices |
|------|--------|
| Language | Python 3 |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript (no framework) |
| Persistence | JSON files (`data/attempts.json`, etc.) |
| CLI | `main.py` + `problem_tracker.py` |

---

## Author

**Nvafeomo K. Konneh** — add your email, LinkedIn, or portfolio link here if you like.

---

## License

MIT License — see [LICENSE](LICENSE) if you add one; otherwise you can paste:

```text
MIT License

Copyright (c) 2026 Nvafeomo K. Konneh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

If you prefer not to ship a separate `LICENSE` file, the paragraph above is enough for many class projects; for GitHub’s license picker, add a `LICENSE` file with the same text.
