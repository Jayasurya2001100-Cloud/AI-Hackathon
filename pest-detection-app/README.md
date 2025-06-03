# 🚀 AI Hackathon - Pest Detection App

Welcome to the AI Hackathon project! This application integrates **FastAPI** (Python backend), **Streamlit** (web UI), and **Flutter** (mobile app) to demonstrate a real-time pest detection solution.

---

## 📁 Project Structure

```
pest-detection-app/
├── backend/
│   └── app.py              # FastAPI backend
├── mobile/
│   ├── streamlit.py        # Streamlit web interface
│   ├── venv/               # Python virtual environment
│   └── flutter/            # Flutter mobile app
```

---

## ⚙️ Prerequisites

- Python 3.8+
- Flutter SDK installed and configured
- PowerShell and Git Bash terminals
- Azure account and Cognitive Services key
- `pip`, `uvicorn`, and `streamlit` installed inside virtual environment

---

## 🔧 Virtual Environment Setup

Navigate to the `mobile/` directory and run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## ▶️ Running the Full Stack App

Use **three separate terminals**:

---

### 1️⃣ Run FastAPI Backend (PowerShell)

```powershell
cd backend
uvicorn app:app --reload
```

> Server will start at `http://127.0.0.1:8000`

---

### 2️⃣ Run Streamlit App (Another PowerShell Terminal)

```powershell
cd mobile
.env\Scripts\Activate
streamlit run streamlit.py
```

> This will open the Streamlit UI in your browser.

---

### 3️⃣ Run Flutter App (Bash Terminal like Git Bash)

```bash
cd mobile/flutter
flutter pub get
flutter run
```

> This will launch the app on your emulator or physical device.

---

## 📝 Notes

- Ensure your `.env` or configuration file includes valid Azure API keys.
- For missing modules, run `pip install <module-name>` inside the activated environment.
- Use `flutter doctor` to verify Flutter setup.

---

## 📬 Contact

For any questions or support, please reach out to the AI Hackathon coordinators.

Happy hacking! 🧠⚡
