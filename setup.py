"""
setup.py — Run once before the event.
───────────────────────────────────────
Creates placeholder reference images in reference_images/ if they don't exist.
Replace these with the real star-location photos before the event.

Usage:
    python setup.py
"""

import os
import numpy as np
import cv2

SETS = {
    "set_a": "A",
    "set_b": "B",
}

def create_placeholder(path: str, label: str):
    """Create a grey 400×400 placeholder with text."""
    img = np.full((400, 400, 3), 60, dtype=np.uint8)
    cv2.putText(img, label, (60, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 0), 2)
    cv2.putText(img, "REPLACE WITH", (80, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 1)
    cv2.putText(img, "REAL PHOTO", (100, 270),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 1)
    cv2.imwrite(path, img)
    print(f"  Created placeholder: {path}")


def main():
    print("=== Treasure Hunt Setup ===\n")

    for folder, label in SETS.items():
        dir_path = os.path.join("reference_images", folder)
        os.makedirs(dir_path, exist_ok=True)

        for i in range(1, 7):
            img_path = os.path.join(dir_path, f"clue_{i}.jpg")
            if os.path.exists(img_path):
                print(f"  [EXISTS] {img_path}")
            else:
                create_placeholder(img_path, f"Set {label} Clue {i}")

    os.makedirs("submissions", exist_ok=True)
    print("\n✅ Setup complete.")
    print("\nNEXT STEPS:")
    print("  1. Replace reference_images/set_a/clue_N.jpg with real star photos.")
    print("  2. Replace reference_images/set_b/clue_N.jpg with real star photos.")
    print("  3. Edit clues.py to update clue text.")
    print("  4. Run:  streamlit run app.py")
    print("  5. Admin: streamlit run admin/leaderboard.py\n")


if __name__ == "__main__":
    main()