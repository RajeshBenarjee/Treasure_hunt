"""
storage_utils.py
────────────────
CSV-based persistence for metadata, scores, and submission state.
Thread-safe enough for a local event (file-level locking via append mode).
"""

import os
import csv
from datetime import datetime

SUBMISSIONS_DIR = "submissions"
METADATA_CSV    = "submissions/metadata.csv"
SCORES_CSV      = "submissions/scores.csv"

# ─── Ensure CSV headers exist ────────────────────────────────────────────────────
def _ensure_metadata_csv():
    if not os.path.exists(METADATA_CSV):
        os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
        with open(METADATA_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["team_id", "clue_set", "start_time", "end_time",
                             "duration_seconds"])

def _ensure_scores_csv():
    if not os.path.exists(SCORES_CSV):
        os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
        with open(SCORES_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["team_id", "clue_set", "correct_count",
                             "start_time", "end_time", "duration_seconds"])


# ─── Public API ─────────────────────────────────────────────────────────────────
def is_team_submitted(team_id: int) -> bool:
    """Check if a team folder already exists and has all 6 images."""
    team_dir = os.path.join(SUBMISSIONS_DIR, str(team_id))
    if not os.path.isdir(team_dir):
        return False
    images = [f for f in os.listdir(team_dir)
              if f.startswith("clue_") and f.endswith(".jpg")]
    return len(images) >= 6


def save_metadata(team_id: int, clue_set: str,
                  start_time: datetime, end_time: datetime):
    """Append one row to metadata.csv."""
    _ensure_metadata_csv()
    duration = (end_time - start_time).total_seconds()
    with open(METADATA_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            team_id,
            clue_set,
            start_time.isoformat(timespec="seconds"),
            end_time.isoformat(timespec="seconds"),
            round(duration, 1),
        ])


def save_score(team_id: int, clue_set: str, correct_count: int,
               start_time: datetime, end_time: datetime):
    """Append one row to scores.csv."""
    _ensure_scores_csv()
    duration = (end_time - start_time).total_seconds()
    with open(SCORES_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            team_id,
            clue_set,
            correct_count,
            start_time.isoformat(timespec="seconds"),
            end_time.isoformat(timespec="seconds"),
            round(duration, 1),
        ])


def load_scores() -> list[dict]:
    """
    Load all rows from scores.csv.
    Returns list of dicts with keys:
      team_id, clue_set, correct_count, start_time, end_time, duration_seconds
    """
    _ensure_scores_csv()
    rows = []
    with open(SCORES_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["correct_count"]    = int(row["correct_count"])
            row["duration_seconds"] = float(row["duration_seconds"])
            rows.append(row)
    return rows


def load_metadata() -> list[dict]:
    """Load all rows from metadata.csv."""
    _ensure_metadata_csv()
    rows = []
    with open(METADATA_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["duration_seconds"] = float(row["duration_seconds"])
            rows.append(row)
    return rows