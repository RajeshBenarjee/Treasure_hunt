"""
admin/leaderboard.py
────────────────────
Run from the project root:
    streamlit run admin/leaderboard.py

Or as a plain script for terminal output:
    python admin/leaderboard.py

Provides:
  • Live leaderboard sorted by (correct DESC, duration ASC)
  • Ability to recalculate scores from saved images
  • Submission browser
"""

import sys
import os

# Allow imports from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import streamlit as st
import pandas as pd
from datetime import datetime

from storage_utils import load_scores, load_metadata
from image_utils import load_reference_images, compare_images, SIMILARITY_THRESHOLD

SUBMISSIONS_DIR = "submissions"
SCORES_CSV      = "submissions/scores.csv"


# ════════════════════════════════════════════════════════════
#  RECALCULATE — scan saved images and recompute scores
# ════════════════════════════════════════════════════════════
def recalculate_all_scores():
    """
    Walk submissions/{team_id}/clue_N.jpg for every team,
    re-run ORB comparison against reference images, overwrite scores.csv.
    """
    ref_images = load_reference_images()
    metadata   = {row["team_id"]: row for row in load_metadata()}
    results    = []

    for team_folder in sorted(os.listdir(SUBMISSIONS_DIR)):
        team_path = os.path.join(SUBMISSIONS_DIR, team_folder)
        if not os.path.isdir(team_path) or not team_folder.isdigit():
            continue

        team_id   = int(team_folder)
        meta      = metadata.get(str(team_id), {})
        clue_set  = meta.get("clue_set", "A" if team_id % 2 else "B")
        correct   = 0

        for clue_num in range(1, 7):
            img_path = os.path.join(team_path, f"clue_{clue_num}.jpg")
            if not os.path.exists(img_path):
                continue
            ref_key = f"{clue_set.lower()}_clue_{clue_num}"
            if ref_key not in ref_images:
                continue
            with open(img_path, "rb") as f:
                score = compare_images(f.read(), ref_images[ref_key])
            if score >= SIMILARITY_THRESHOLD:
                correct += 1

        results.append({
            "team_id":          team_id,
            "clue_set":         clue_set,
            "correct_count":    correct,
            "start_time":       meta.get("start_time", ""),
            "end_time":         meta.get("end_time",   ""),
            "duration_seconds": meta.get("duration_seconds", 0),
        })

    # Overwrite scores.csv
    if results:
        os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
        with open(SCORES_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    return results


# ════════════════════════════════════════════════════════════
#  LEADERBOARD BUILDER
# ════════════════════════════════════════════════════════════
def build_leaderboard(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["team_id"]       = df["team_id"].astype(str)
    df["correct_count"] = df["correct_count"].astype(int)
    df["duration_seconds"] = df["duration_seconds"].astype(float)

    # Sort: most correct first, fastest second
    df = df.sort_values(
        ["correct_count", "duration_seconds"],
        ascending=[False, True],
    ).reset_index(drop=True)

    df.index += 1  # rank starts at 1

    # Format duration
    df["duration"] = df["duration_seconds"].apply(
        lambda s: f"{int(s//60)}m {int(s%60)}s"
    )

    return df[["team_id", "clue_set", "correct_count", "duration"]]


# ════════════════════════════════════════════════════════════
#  TERMINAL MODE (no Streamlit)
# ════════════════════════════════════════════════════════════
def print_leaderboard():
    rows = load_scores()
    df   = build_leaderboard(rows)
    if df.empty:
        print("No submissions yet.")
    else:
        print("\n══════════════ LEADERBOARD ══════════════")
        print(df.to_string())
        print("═════════════════════════════════════════\n")


# ════════════════════════════════════════════════════════════
#  STREAMLIT ADMIN UI
# ════════════════════════════════════════════════════════════
if __name__ == "__main__" and "streamlit" not in sys.modules:
    print_leaderboard()
else:
    st.set_page_config(page_title="Admin — Treasure Hunt", layout="wide")
    st.title("🏆 Admin Dashboard — Tech Treasure Hunt")

    tab1, tab2, tab3 = st.tabs(["Leaderboard", "Recalculate Scores", "Raw Data"])

    # ── Tab 1: Live Leaderboard ──
    with tab1:
        st.subheader("Current Leaderboard")
        st.caption("Ranked by correct answers (desc) then completion time (asc).")

        if st.button("🔄 Refresh"):
            st.rerun()

        rows = load_scores()
        df   = build_leaderboard(rows)

        if df.empty:
            st.info("No submissions recorded yet.")
        else:
            st.dataframe(
                df.rename(columns={
                    "team_id":       "Team ID",
                    "clue_set":      "Set",
                    "correct_count": "✅ Correct",
                    "duration":      "⏱ Time",
                }),
                use_container_width=True,
                height=min(600, 80 + len(df) * 35),
            )
            st.metric("Total teams submitted", len(df))

    # ── Tab 2: Recalculate ──
    with tab2:
        st.subheader("Recalculate Scores from Saved Images")
        st.warning("This overwrites the current scores.csv. Use after adding/replacing reference images.")

        if st.button("⚙️ Recalculate All Scores"):
            with st.spinner("Processing all submissions..."):
                results = recalculate_all_scores()
            st.success(f"Done — recalculated {len(results)} team(s).")
            df2 = build_leaderboard(results)
            if not df2.empty:
                st.dataframe(df2, use_container_width=True)

    # ── Tab 3: Raw Data ──
    with tab3:
        st.subheader("Raw Metadata")
        meta = load_metadata()
        if meta:
            st.dataframe(pd.DataFrame(meta), use_container_width=True)
        else:
            st.info("No metadata yet.")

        st.subheader("Raw Scores")
        scores = load_scores()
        if scores:
            st.dataframe(pd.DataFrame(scores), use_container_width=True)
        else:
            st.info("No scores yet.")

        # Download buttons
        if meta:
            meta_csv = pd.DataFrame(meta).to_csv(index=False)
            st.download_button("⬇ Download metadata.csv", meta_csv,
                               "metadata.csv", "text/csv")
        if scores:
            scores_csv = pd.DataFrame(scores).to_csv(index=False)
            st.download_button("⬇ Download scores.csv", scores_csv,
                               "scores.csv", "text/csv")