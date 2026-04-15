# 🧭 Tech Treasure Hunt

An interactive **offline treasure hunt platform** built using **Streamlit** for college technical events.  
Teams explore real-world locations, capture images, and validate their progress through **computer vision-based verification (OpenCV ORB)**.

---

## 🚀 Features

### 🎯 Core Functionality

- 📸 **Image-Based Treasure Hunt**
  - Teams capture photos at clue locations
  - Submit via web app for verification

- 🧠 **Computer Vision Validation**
  - Uses **OpenCV (ORB feature matching)** to compare submitted images with reference images

- 🔀 **Dual Hunt Tracks**
  - Supports **Set A & Set B**
  - Enables multiple teams to play simultaneously without overlap

---

## 🛡️ Anti-Cheat Mechanisms

- 📷 **Camera-only input**
  - Uses `st.camera_input` to block gallery uploads

- 🔒 **Single Submission Rule**
  - One valid submission per Team ID

- 🚫 **Upload Limit**
  - Locked after **6 submissions**

- 🤫 **Hidden Scoring**
  - Scores stored securely and not visible to participants

- 🧩 **Strict Mapping**
  - Each clue corresponds to exactly one upload slot

---

## 🧑‍💻 Admin Controls

- 📊 **Leaderboard Dashboard**
  - Monitor team progress in real-time
  - Track scores and submissions

- ⚙️ **Configurable Setup**
  - Customize:
    - Clue text
    - Reference images
    - Similarity thresholds
    - ORB feature parameters

---

## ⚙️ Tech Stack

- **Frontend & Backend**: Streamlit  
- **Computer Vision**: OpenCV (ORB Feature Matching)  
- **Language**: Python  

---

## 🧩 How It Works

1. Teams open the Streamlit app  
2. Enter their **Team ID**  
3. Receive clues from admin  
4. Travel to physical locations  
5. Capture and submit images  
6. System verifies images using OpenCV  
7. Scores are recorded  
8. Admin monitors progress via dashboard  

---

## 📁 Project Structure

```
treasure_hunt/
├── app.py                    # Main Streamlit app (RUN THIS)
├── clues.py                  # Edit clue text here
├── image_utils.py            # OpenCV comparison logic
├── storage_utils.py          # CSV read/write helpers
├── setup.py                  # One-time setup script
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Theme + performance settings
├── admin/
│   └── leaderboard.py        # Admin dashboard (run separately)
├── reference_images/
│   ├── set_a/
│   │   ├── clue_1.jpg
│   │   ├── clue_2.jpg
│   │   └── ... (clue_3 → clue_6)
│   └── set_b/
│       ├── clue_1.jpg
│       └── ... (clue_2 → clue_6)
└── submissions/              # Auto-created on first run
    ├── metadata.csv
    ├── scores.csv
    └── {team_id}/
        ├── clue_1.jpg
        └── ... (clue_2 → clue_6)
```

---

## 📦 Installation

```bash
git clone https://github.com/RajeshBenarjee/Treasure_hunt.git
cd Treasure_hunt
pip install -r requirements.txt
```

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. One-time setup (creates placeholder reference images)
python setup.py

# 3. Replace with REAL location images
# reference_images/set_a/clue_1.jpg ... clue_6.jpg
# reference_images/set_b/clue_1.jpg ... clue_6.jpg

# 4. Edit clues
# Modify clues.py

# 5. Run main app
streamlit run app.py

# 6. Run admin dashboard (separate terminal)
streamlit run admin/leaderboard.py --server.port 8502
```

---

## ⚙️ Key Configuration

| Setting                | File             | Variable                  |
|----------------------|------------------|---------------------------|
| Similarity Threshold | image_utils.py   | `SIMILARITY_THRESHOLD = 15` |
| Image Resize         | image_utils.py   | `TARGET_SIZE = (400, 400)` |
| ORB Features         | image_utils.py   | `MAX_ORB_FEATURES = 500` |
| Clue Text            | clues.py         | `CLUE_SET_A`, `CLUE_SET_B` |

---

## 📈 Scalability

- Supports **500+ concurrent users**
- Efficient ORB-based image matching
- Lightweight Streamlit deployment

### 🚀 Production Recommendations

- Run with:
  ```bash
  streamlit run app.py --server.maxMessageSize 20
  ```
- Use:
  - ≥ **4 CPU cores**
  - ≥ **8 GB RAM**
- For scaling:
  - Deploy using **NGINX + Streamlit**
  - Optional: **Gunicorn for load balancing**

---

## 🎯 Use Cases

- 🎓 College Technical Fests  
- 🧑‍🏫 Campus Orientation Programs  
- 🕵️ Scavenger Hunt Events  
- 🧩 Team-Building Activities  

---

## 🔮 Future Improvements

- Live leaderboard for participants  
- GPS-based validation  
- AI-based advanced image recognition  
- Mobile app version  

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository  
2. Create a new branch  
3. Make changes  
4. Submit a Pull Request  

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Rajesh Benarjee**  
🔗 GitHub: https://github.com/RajeshBenarjee
