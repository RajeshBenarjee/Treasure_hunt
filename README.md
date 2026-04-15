# 🗺️ Tech Treasure Hunt — Streamlit App

A complete offline treasure hunt platform for college technical events.

---

## Folder Structure

```
treasure_hunt/
├── app.py                    ← Main Streamlit app  (RUN THIS)
├── clues.py                  ← Edit clue text here
├── image_utils.py            ← OpenCV comparison logic
├── storage_utils.py          ← CSV read/write helpers
├── setup.py                  ← One-time setup script
├── requirements.txt
├── .streamlit/
│   └── config.toml           ← Theme + performance settings
├── admin/
│   └── leaderboard.py        ← Admin dashboard  (run separately)
├── reference_images/
│   ├── set_a/
│   │   ├── clue_1.jpg        ← REPLACE with real star photos
│   │   ├── clue_2.jpg
│   │   └── ... (clue_3 → clue_6)
│   └── set_b/
│       ├── clue_1.jpg
│       └── ... (clue_2 → clue_6)
└── submissions/              ← Auto-created on first run
    ├── metadata.csv
    ├── scores.csv
    └── {team_id}/
        ├── clue_1.jpg
        └── ... (clue_2 → clue_6)
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. One-time setup (creates placeholder reference images)
python setup.py

# 3. Replace reference images with REAL photos of star locations
#    reference_images/set_a/clue_1.jpg  ... clue_6.jpg
#    reference_images/set_b/clue_1.jpg  ... clue_6.jpg

# 4. Edit clues in clues.py

# 5. Run the app
streamlit run app.py

# 6. Admin leaderboard (separate terminal)
streamlit run admin/leaderboard.py --server.port 8502
```

---

## Key Settings

| Setting | File | Variable |
|---|---|---|
| Similarity threshold | `image_utils.py` | `SIMILARITY_THRESHOLD = 15` |
| Image resize | `image_utils.py` | `TARGET_SIZE = (400, 400)` |
| ORB features | `image_utils.py` | `MAX_ORB_FEATURES = 500` |
| Clue text | `clues.py` | `CLUE_SET_A`, `CLUE_SET_B` |

---

## Anti-Cheat Summary

- Camera-only input (`st.camera_input`) — no gallery access
- One submission per Team ID (checked before entry)
- Locked after 6 uploads (no further changes)
- Each clue strictly maps to one upload slot
- No scores/feedback shown to participants
- Scores stored silently in CSV

---

## For 500 Concurrent Users

- Use `streamlit run app.py --server.maxMessageSize 20`
- Deploy on a machine with ≥ 4 CPU cores, ≥ 8 GB RAM
- Consider `gunicorn` + `streamlit` behind nginx for production scale
- All state is per-session (no shared mutable state)