# 🤖 AI Recruiter

**AI Recruiter** is an intelligent resume screening and candidate analysis system powered by **Google Gemini LLM**. It helps HR teams automate the screening process, reduce bias with Blind Hiring, and make data-driven decisions.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)

## ✨ Key Features
- **Dual AI Engines**: Choose between High-Speed Rule-Based or Advanced LLM (Gemini) analysis.
- **Blind Hiring Mode**: Anonymize candidate data to reduce unconscious bias.
- **Candidate Battle Arena**: Compare two candidates side-by-side.
- **Auto-Generated Interviews**: Get tailored interview questions based on resume gaps.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9 or higher
- A Google Cloud API Key (for Gemini LLM features)

### 1. Clone & Setup
```bash
git clone https://github.com/Thanarat-Int/AI-ProjectX.git
cd "AI-ProjectX/AI Recruiter"
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the root directory (`AI Recruiter/`) and add your API key:
```ini
GOOGLE_API_KEY=your_api_key_here
```
> *Note: If you don't have an API key, you can still use the "Rule-Based" engine.*

---

## 🚀 Usage Guide

### Run the Application
Start the Streamlit web server:
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

### How to Use
1.  **Dashboard**:
    *   **Context**: Select Department & Seniority level from the sidebar.
    *   **Upload**: Paste the Job Description (JD) and drag & drop Resume PDFs.
    *   **Analyze**: Click "Start Analysis".
2.  **Comparison**: Go to "Compare Candidates" in the sidebar to view a head-to-head match.
3.  **History**: View past analysis logs and export data to CSV in the "History Logs" section.

---

## 🐳 Running with Docker
If you prefer using Docker:

```bash
# Build
docker build -t ai-recruiter .

# Run (Make sure to pass the API Key)
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here ai-recruiter
```

---

## � Project Structure
```
AI Recruiter/
├── data/               # Verified credentials & sample resumes
├── src/                # Core logic (analyzer, parser, db)
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── presentTH.md        # Project details (Thai)
└── presentEN.md        # Project details (English)
```
