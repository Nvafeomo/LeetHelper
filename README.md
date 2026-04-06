# LeetTracker

Web app for tracking LeetCode practice: browse a catalog from a `leetcode.json` export, log attempts (time, approach, solved, notes), filter attempts by topic and text, and view simple stats. Optional **Blind 75** list and topic tags. There’s also a small **CLI** (`main.py`) for a manual problem list.

I built it to stay accountable while grinding problems and to practice Python, Flask, and plain HTML/CSS/JS. A popular suggestion I always hear from content creators to track leetcode progress and track attempt info(number of attempts and time taken). Most of them recomment using an except spreadsheet to sort the problems and log attempt data but i believe a site like this is a better alternative.

## Features

- **Accounts:** register, log in, log out; attempts and stats are **per user** (session cookies + CSRF on writes).
- Catalog with sort, title filter, pagination; optional **Blind 75** (`data/blind75.json`)
- Per-user attempts + optional **topic tags** (`data/problem_topics.json`)
- **Attempts** tab: all attempts with optional filters by problem name, topic, and approach/reflection; stats (fastest first timed attempt per difficulty, topic times, per-problem time)
- JSON **API** under `/api/…` (same app powers the UI)

## Stack

**Python · Flask · SQLAlchemy · Flask-Login · Flask-WTF (CSRF)** — front end is plain HTML/CSS/JS. The **catalog** still comes from JSON on disk (`data/leetcode.json`, topics, blind list). **Attempts** are stored in a **database** (SQLite file by default, or PostgreSQL via `DATABASE_URL`).

Legacy **`data/attempts.json`** is no longer used by the web app; you can import it into a user account with `python scripts/import_attempts_json.py USERNAME` (see below).

## Run locally

```bash
pip install -r requirements.txt
```

Put **`data/leetcode.json`** in place (LeetCode `stat_status_pairs` export). Set a **secret key** for sessions (required outside debug):

```bash
set SECRET_KEY=your-random-secret
python app.py
```

(On Unix: `export SECRET_KEY=...`.)

Open http://127.0.0.1:5000 — **Register** an account in the header, then use Attempts / Stats. The SQLite file is created at **`data/leetcodetracker.db`** on first run.

**Optional:** import old flat JSON attempts (from before the DB) after you register:

`python scripts/import_attempts_json.py your_username`

CLI: `python main.py` (still uses `data/problems.json` for the legacy flow).

## Project layout

```
app.py              # Flask + routes
auth.py             # /api/auth (register, login, logout, me)
extensions.py       # db, login_manager, csrf
models.py           # User, Attempt
main.py             # CLI
templates/          # index.html
static/             # app.js, style.css
utils/              # catalog, storage (legacy JSON), storage_db (attempts), time parsing
problems/           # optional: per-problem JSON dumps (topics, description, …)
data/               # leetcode.json, blind75.json, problem_topics.json, leetcodetracker.db, …
scripts/            # import_attempts_json, build_problem_topics_from_problems, …
```

**Topic tags:** If you have a `problems/` folder of LeetCode JSON files, regenerate `data/problem_topics.json` (skips SQL-only and Shell-only problems):

`python scripts/build_problem_topics_from_problems.py`

## Deploy (e.g. Railway)

Use a production server, not `python app.py`. The repo includes a **`Procfile`** so platforms like Railway can start with:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

(`$PORT` is set by the host.) Install deps with `pip install -r requirements.txt` (includes **gunicorn**).

**Environment variables**

- **`SECRET_KEY`** — required for secure sessions (set a long random string).
- **`DATABASE_URL`** — optional; if unset, SQLite is used at `data/leetcodetracker.db`. On Railway, add a **PostgreSQL** plugin and use its `DATABASE_URL` (the app normalizes `postgres://` to `postgresql://`).

Mount **persistent storage** on **`data/`** so the SQLite file (or any local JSON) survives redeploys, **or** use Postgres only and ensure `data/leetcode.json` (and related files) are present via the image or a volume.

With **SQLite**, use **one** Gunicorn worker, or switch to Postgres for multiple workers.

## Screenshots

| Catalog | Attempts |
| --- | --- |
| ![Catalog](docs/screenshots/catalog.png) | ![Attempts](docs/screenshots/attempts.png) |

| Problem / attempt log | Stats |
| --- | --- |
| ![Attempt log](docs/screenshots/attemptlog.png) | ![Stats](docs/screenshots/stats.png) |

## Ideas

Charts, CSV export, LeetCode import helper, tests.

## Author

**Nvafeomo K. Konneh**

- **Email:** [nvafeomo05@gmail.com](mailto:nvafeomo05@gmail.com)
- **Phone:** 267-461-8268
- **LinkedIn:** [Nvafeomo Konneh](https://www.linkedin.com/in/nvafeomo-konneh-a6a1a9367)
## License

MIT
