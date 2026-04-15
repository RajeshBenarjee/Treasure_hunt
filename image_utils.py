"""
image_utils.py
──────────────
OpenCV-based image comparison helpers.
Reference images are loaded once and cached.
"""

import os
import cv2
import numpy as np
from PIL import Image
import io

# ─── Config ─────────────────────────────────────────────────────────────────────
TARGET_SIZE       = (400, 400)   # resize all images before comparison
SIMILARITY_THRESHOLD = 15        # minimum ORB matches to count as "correct"
MAX_ORB_FEATURES  = 500          # ORB detector feature count
SUBMISSIONS_DIR   = "submissions"
REFERENCE_DIR     = "reference_images"


# ─── Reference image loader ─────────────────────────────────────────────────────
def load_reference_images() -> dict:
    """
    Walk reference_images/{set_a,set_b}/ and load all .jpg/.png files.
    Returns dict keyed as  "a_clue_1", "b_clue_3", etc.
    Gracefully skips missing folders.
    """
    ref = {}
    for set_name in ("set_a", "set_b"):
        folder = os.path.join(REFERENCE_DIR, set_name)
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            # Expect filenames like clue_1.jpg, clue_2.jpg …
            stem = os.path.splitext(fname)[0]          # "clue_1"
            key  = f"{set_name[4]}_{stem}"             # "a_clue_1"
            path = os.path.join(folder, fname)
            img  = _load_and_preprocess(path)
            if img is not None:
                ref[key] = img
    return ref


def _load_and_preprocess(source) -> np.ndarray | None:
    """
    Load an image from a file path or bytes, resize and convert to grayscale.
    Returns None on failure.
    """
    try:
        if isinstance(source, (str, os.PathLike)):
            img = cv2.imread(str(source))
        else:
            # bytes / BytesIO
            arr  = np.frombuffer(source, np.uint8)
            img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if img is None:
            return None

        img = cv2.resize(img, TARGET_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    except Exception:
        return None


# ─── ORB comparison ─────────────────────────────────────────────────────────────
def compare_images(submitted_bytes: bytes, reference_gray: np.ndarray) -> int:
    """
    Compare a submitted image (raw bytes) against a preprocessed reference.
    Returns the number of good ORB feature matches (higher = more similar).
    Returns 0 on any error.
    """
    try:
        submitted_gray = _load_and_preprocess(submitted_bytes)
        if submitted_gray is None or reference_gray is None:
            return 0

        orb     = cv2.ORB_create(nfeatures=MAX_ORB_FEATURES)
        kp1, d1 = orb.detectAndCompute(submitted_gray,  None)
        kp2, d2 = orb.detectAndCompute(reference_gray, None)

        if d1 is None or d2 is None or len(d1) == 0 or len(d2) == 0:
            return 0

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(d1, d2)
        # Filter by distance (keep only good matches)
        good    = [m for m in matches if m.distance < 64]
        return len(good)
    except Exception:
        return 0


# ─── Save uploaded image ─────────────────────────────────────────────────────────
def save_submission_image(team_id: int, clue_num: int, img_bytes: bytes) -> str:
    """
    Save raw image bytes to submissions/{team_id}/clue_{n}.jpg
    Converts to JPEG for consistent storage.
    Returns the saved file path.
    """
    team_dir = os.path.join(SUBMISSIONS_DIR, str(team_id))
    os.makedirs(team_dir, exist_ok=True)

    out_path = os.path.join(team_dir, f"clue_{clue_num}.jpg")

    # Convert to PIL → save as JPEG (normalises format)
    pil_img  = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    pil_img.save(out_path, "JPEG", quality=85)
    return out_path