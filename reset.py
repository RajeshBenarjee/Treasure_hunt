"""
reset.py — Run this BEFORE the competition starts to wipe all test data.
─────────────────────────────────────────────────────────────────────────
Usage:
    python reset.py           ← asks for confirmation
    python reset.py --force   ← skips confirmation (use carefully!)
"""

import os
import sys
import shutil
import csv

SUBMISSIONS_DIR = "submissions"
METADATA_CSV    = os.path.join(SUBMISSIONS_DIR, "metadata.csv")
SCORES_CSV      = os.path.join(SUBMISSIONS_DIR, "scores.csv")


def reset(force: bool = False):
    print("\n" + "═" * 50)
    print("   TREASURE HUNT — RESET TOOL")
    print("═" * 50)

    # Show current state
    teams = []
    if os.path.isdir(SUBMISSIONS_DIR):
        teams = [d for d in os.listdir(SUBMISSIONS_DIR)
                 if os.path.isdir(os.path.join(SUBMISSIONS_DIR, d))]

    print(f"\n  Submitted teams found : {len(teams)}")
    if teams:
        print(f"  Team IDs             : {', '.join(sorted(teams))}")
    print(f"  metadata.csv exists  : {os.path.exists(METADATA_CSV)}")
    print(f"  scores.csv exists    : {os.path.exists(SCORES_CSV)}")

    if not teams and not os.path.exists(METADATA_CSV):
        print("\n  ✅ Already clean — nothing to reset.\n")
        return

    if not force:
        print("\n  ⚠️  This will DELETE all submissions and scores.")
        confirm = input("  Type  YES  to confirm: ").strip()
        if confirm != "YES":
            print("  Cancelled.\n")
            return

    # ── Delete all team folders ──────────────────────────────────────────────
    deleted_teams = 0
    for team_dir in teams:
        full_path = os.path.join(SUBMISSIONS_DIR, team_dir)
        shutil.rmtree(full_path, ignore_errors=True)
        deleted_teams += 1

    # ── Wipe CSV files (keep headers only) ──────────────────────────────────
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)

    with open(METADATA_CSV, "w", newline="") as f:
        csv.writer(f).writerow(
            ["team_id", "clue_set", "start_time", "end_time", "duration_seconds"]
        )

    with open(SCORES_CSV, "w", newline="") as f:
        csv.writer(f).writerow(
            ["team_id", "clue_set", "correct_count",
             "start_time", "end_time", "duration_seconds"]
        )

    print(f"\n  ✅ Reset complete!")
    print(f"     Deleted {deleted_teams} team folder(s)")
    print(f"     metadata.csv cleared")
    print(f"     scores.csv cleared\n")
    print("  🚀 App is ready for the competition.\n")


if __name__ == "__main__":
    force = "--force" in sys.argv
    reset(force=force)