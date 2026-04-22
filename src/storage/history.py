from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
from ..models import DailyBrief, CEOReport


def save_brief(history_dir: str, brief: DailyBrief) -> Path:
    out = Path(history_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{brief.brief_date.isoformat()}.brief.json"
    path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    return path


def save_report(history_dir: str, report: CEOReport) -> Path:
    out = Path(history_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{report.brief_date.isoformat()}.report.json"
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_recent_briefs(history_dir: str, days: int, before: date) -> list[DailyBrief]:
    out = Path(history_dir)
    if not out.exists():
        return []
    briefs: list[DailyBrief] = []
    for offset in range(1, days + 1):
        d = before - timedelta(days=offset)
        path = out / f"{d.isoformat()}.brief.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            briefs.append(DailyBrief.model_validate(data))
    briefs.reverse()
    return briefs
