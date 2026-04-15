"""
╔══════════════════════════════════════════════════════════╗
║         TECHNICAL TREASURE HUNT — MAIN APP              ║
║  Run: streamlit run app.py                               ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os
import csv
from datetime import datetime
from PIL import Image
import io

from image_utils import (
    load_reference_images,
    compare_images,
    save_submission_image,
    SIMILARITY_THRESHOLD,
)
from clues import CLUE_SET_A, CLUE_SET_B
from storage_utils import (
    is_team_submitted,
    save_metadata,
    save_score,
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tech Treasure Hunt",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base theme */
    .stApp { background-color: #0d0d0d; color: #f0f0f0; }
    .main .block-container { padding: 1.5rem 1rem; max-width: 680px; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Headings */
    h1 { font-size: 1.8rem !important; color: #FFD700 !important; letter-spacing: 2px; }
    h2 { font-size: 1.2rem !important; color: #FFD700 !important; }
    h3 { font-size: 1rem !important; color: #aaa !important; }

    /* Clue cards */
    .clue-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-left: 3px solid #FFD700;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }
    .clue-text { color: #e0e0e0; font-size: 0.95rem; line-height: 1.5; }
    .clue-num  { color: #FFD700; font-weight: 700; font-size: 0.8rem;
                 letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }

    /* Status indicators */
    .status-done    { color: #4CAF50; font-size: 0.8rem; font-weight: 600; }
    .status-pending { color: #888;    font-size: 0.8rem; }

    /* Progress bar wrapper */
    .progress-label { color: #aaa; font-size: 0.8rem; margin-bottom: 4px; }

    /* Completion banner */
    .done-banner {
        background: linear-gradient(135deg, #1a2a1a, #0d1a0d);
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-top: 1rem;
    }
    .done-banner h2 { color: #4CAF50 !important; font-size: 1.5rem !important; }
    .done-banner p  { color: #aaa; }

    /* Button styling */
    .stButton > button {
        background: #FFD700; color: #000;
        border: none; border-radius: 6px;
        font-weight: 700; font-size: 0.9rem;
        padding: 0.5rem 1.5rem;
        width: 100%;
    }
    .stButton > button:hover { background: #FFC200; }

    /* Camera input */
    [data-testid="stCameraInput"] { border-radius: 8px; overflow: hidden; }

    /* Divider */
    hr { border-color: #222; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "team_id": None,
        "clue_set": None,
        "clues": [],
        "images": {},          # clue_index → PIL Image
        "scores": {},          # clue_index → bool
        "submitted": False,
        "start_time": None,
        "end_time": None,
        "camera_keys": {i: 0 for i in range(6)},  # for retake reset
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── Reference Images (cached) ──────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_reference_images():
    return load_reference_images()

ref_images = get_reference_images()


# ─── Helper: assign clue set ────────────────────────────────────────────────────
def assign_clue_set(team_id: int):
    if team_id % 2 == 1:
        return "A", CLUE_SET_A
    else:
        return "B", CLUE_SET_B


# ─── Helper: process one uploaded image ─────────────────────────────────────────
def process_upload(clue_idx: int, img_bytes: bytes):
    """Save image, run comparison, store result — all silently."""
    team_id = st.session_state.team_id
    clue_set = st.session_state.clue_set

    # Save to disk
    save_submission_image(team_id, clue_idx + 1, img_bytes)

    # Load as PIL for preview
    pil_img = Image.open(io.BytesIO(img_bytes))
    st.session_state.images[clue_idx] = pil_img

    # Compare with reference (silent — never shown to user)
    ref_key = f"{clue_set.lower()}_clue_{clue_idx + 1}"
    if ref_key in ref_images:
        score = compare_images(img_bytes, ref_images[ref_key])
        st.session_state.scores[clue_idx] = (score >= SIMILARITY_THRESHOLD)
    else:
        # No reference image → treat as wrong (or skip)
        st.session_state.scores[clue_idx] = False


# ─── Helper: auto-submit ────────────────────────────────────────────────────────
def auto_submit():
    team_id   = st.session_state.team_id
    clue_set  = st.session_state.clue_set
    start     = st.session_state.start_time
    end       = datetime.now()
    st.session_state.end_time = end

    correct = sum(1 for v in st.session_state.scores.values() if v)

    save_metadata(team_id, clue_set, start, end)
    save_score(team_id, clue_set, correct, start, end)
    st.session_state.submitted = True


# ════════════════════════════════════════════════════════════
#  SCREEN 1 — TEAM ID ENTRY
# ════════════════════════════════════════════════════════════
def screen_team_entry():
    st.markdown("# 🗺️ Tech Treasure Hunt")
    st.markdown("<p style='color:#888; margin-top:-10px;'>Find the stars. Capture the proof.</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    team_id_str = st.text_input(
        "Enter your Team ID",
        placeholder="e.g. 42",
        max_chars=6,
        key="team_id_input",
    )

    if st.button("Start Hunt →"):
        if not team_id_str.strip().isdigit():
            st.error("Please enter a valid numeric Team ID.")
            return

        tid = int(team_id_str.strip())

        if is_team_submitted(tid):
            st.error("⛔ This team has already submitted. No re-entry allowed.")
            return

        clue_set_label, clues = assign_clue_set(tid)
        st.session_state.team_id   = tid
        st.session_state.clue_set  = clue_set_label
        st.session_state.clues     = clues
        st.session_state.start_time = datetime.now()
        st.rerun()


# ════════════════════════════════════════════════════════════
#  SCREEN 2 — HUNT IN PROGRESS
# ════════════════════════════════════════════════════════════
def screen_hunt():
    team_id  = st.session_state.team_id
    clue_set = st.session_state.clue_set
    clues    = st.session_state.clues
    images   = st.session_state.images

    uploaded_count = len(images)

    # ── Header ──
    st.markdown(f"# 🗺️ Tech Treasure Hunt")
    col1, col2 = st.columns(2)
    col1.markdown(f"**Team:** `{team_id}`")
    col2.markdown(f"**Set:** `{clue_set}`")

    # ── Progress ──
    pct = uploaded_count / 6
    st.markdown(f"<p class='progress-label'>Progress: {uploaded_count}/6 clues captured</p>",
                unsafe_allow_html=True)
    st.progress(pct)
    st.markdown("---")

    # ── Clue Cards ──
    for i, clue_text in enumerate(clues):
        done = i in images

        with st.container():
            status_html = (
                "<span class='status-done'>✔ Captured</span>" if done
                else "<span class='status-pending'>○ Pending</span>"
            )
            st.markdown(f"""
            <div class='clue-card'>
                <div class='clue-num'>Clue {i+1} &nbsp;{status_html}</div>
                <div class='clue-text'>{clue_text}</div>
            </div>
            """, unsafe_allow_html=True)

            if done:
                # Show preview + retake option
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(images[i], width=120, caption="Captured")
                with c2:
                    if st.button(f"↺ Retake #{i+1}", key=f"retake_{i}"):
                        del st.session_state.images[i]
                        if i in st.session_state.scores:
                            del st.session_state.scores[i]
                        # Increment camera key to reset the widget
                        st.session_state.camera_keys[i] += 1
                        st.rerun()
            else:
                # Camera input — unique key prevents ghost state
                cam_key = f"cam_{i}_{st.session_state.camera_keys[i]}"
                photo = st.camera_input(
                    f"📷 Point camera at Clue {i+1} location",
                    key=cam_key,
                    help="Use camera only. Gallery not supported.",
                )
                if photo is not None:
                    with st.spinner("Processing..."):
                        process_upload(i, photo.getvalue())
                    st.rerun()

        st.markdown("")  # spacing

    # ── Auto-submit when all 6 done ──
    if len(st.session_state.images) == 6 and not st.session_state.submitted:
        auto_submit()
        st.rerun()


# ════════════════════════════════════════════════════════════
#  SCREEN 3 — COMPLETION
# ════════════════════════════════════════════════════════════
def screen_done():
    st.markdown("""
    <div class='done-banner'>
        <h2>🏁 Your hunt is completed</h2>
        <p>All 6 clues have been submitted successfully.<br>
        Results will be announced at the end of the event.</p>
        <p style='margin-top:1.5rem; font-size:0.75rem; color:#555;'>
            Team {team_id} • Set {clue_set}
        </p>
    </div>
    """.format(
        team_id=st.session_state.team_id,
        clue_set=st.session_state.clue_set,
    ), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  ROUTER
# ════════════════════════════════════════════════════════════
if st.session_state.submitted:
    screen_done()
elif st.session_state.team_id is None:
    screen_team_entry()
else:
    screen_hunt()