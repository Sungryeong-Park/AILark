import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

PAPER_LIMIT = 5
HF_API_URL = "https://huggingface.co/api/daily_papers"
REPORTS_DIR = Path(__file__).parent.parent / "reports"


def _week_seen_file():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    week_dir = REPORTS_DIR / f"{monday.strftime('%m%d')}-{sunday.strftime('%m%d')}"
    week_dir.mkdir(parents=True, exist_ok=True)
    return week_dir / "seen_papers.json"


def _load_seen():
    path = _week_seen_file()
    return set(json.loads(path.read_text())) if path.exists() else set()


def _save_seen(ids):
    _week_seen_file().write_text(json.dumps(list(ids)))


def fetch_papers(limit=PAPER_LIMIT):
    seen = _load_seen()

    response = requests.get(HF_API_URL, timeout=30)
    response.raise_for_status()

    items = sorted(response.json(), key=lambda x: x["paper"].get("upvotes", 0), reverse=True)

    papers = []
    new_ids = set()
    for item in items:
        p = item["paper"]
        pid = p.get("id", "")
        if pid in seen:
            continue
        papers.append({
            "title": p.get("title", ""),
            "authors": ", ".join(a["name"] for a in p.get("authors", []) if not a.get("hidden")),
            "published": p.get("publishedAt", "")[:10],
            "abstract": p.get("summary", ""),
            "pdf": f"https://arxiv.org/pdf/{pid}",
            "upvotes": p.get("upvotes", 0),
        })
        new_ids.add(pid)
        if len(papers) >= limit:
            break

    _save_seen(seen | new_ids)
    return papers
