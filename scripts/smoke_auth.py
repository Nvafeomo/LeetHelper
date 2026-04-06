"""Quick auth + DB smoke test (run from repo root)."""
import os
import re
import sys
import uuid

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app import app  # noqa: E402

with app.test_client() as c:
    r0 = c.get("/")
    assert r0.status_code == 200
    html = r0.get_data(as_text=True)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    tok = m.group(1) if m else ""
    h = {"X-CSRFToken": tok, "Content-Type": "application/json"}
    uname = f"u_{uuid.uuid4().hex[:10]}"
    r = c.post(
        "/api/auth/register",
        json={"username": uname, "password": "smokepass1"},
        headers=h,
    )
    print("register", r.status_code, r.get_json())
    r2 = c.get("/api/auth/me")
    print("me", r2.status_code, r2.get_json())
    r3 = c.get("/api/attempts")
    print("attempts", r3.status_code, len(r3.get_json() or []))
