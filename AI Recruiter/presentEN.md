# 🚀 AI Resume Screener & Interview Assistant
**World-Class Intelligent Recruitment System**

---

## 📖 Project Overview

This project is an advanced **AI-powered Recruitment System** designed to streamline the hiring process. It automates resume screening, scores candidates against job descriptions, and provides deep insights to help HR teams make data-driven decisions. Built with Python and Streamlit, it offers a production-grade UI with features like Blind Hiring, Candidate Comparison, and Automated Email Actions.

---

## 🌟 Key Features

### 1. 🧠 Hybrid AI Engine
We utilize a dual-engine approach to deliver the best results:
- **Rule-Based Engine (Basic & Fast)**: Uses privacy-focused keyword matching and Regex based on a comprehensive dictionary of 150+ skills (Tech, Business, Design). Ensures 100% accuracy for scoring Hard Skills.
- **Gemini LLM Engine (Advanced & Intelligent)**: Leverages Google's Gemini Pro AI for deep semantic analysis. It acts like a senior HR professional, summarizing profiles and generating personalized interview questions using Full Context Injection.

### 2. 📂 Bulk Screening & Live Leaderboard
Supports drag-and-drop upload for multiple PDF/DOCX resumes. The system processes them in real-time capable of ranking candidates on a comprehensive "Live Leaderboard" with color-coded scores, providing an instant overview of candidate quality.

### 3. 🎯 Department Presets & Dynamic Weighting
Includes pre-configured presets for various departments (e.g., Sales, Engineering, Finance, HR). HR professionals can also define custom "Essential Skills" that carry double the weight in scoring, ensuring the most relevant candidates rise to the top.

### 4. 🙈 Blind Hiring Mode
A toggle feature to mask candidate names and sensitive information (e.g., displaying "Candidate #1"). This ensures hiring decisions are based purely on skills and merit, significantly reducing unconscious bias.

### 5. ⚔️ Comparison Battle Arena
A dedicated comparison tool to pit two candidates head-to-head. Visualizes their scores, skills, and analytics side-by-side, making it easy to determine the better fit when candidates have similar scores.

### 6. 📧 Smart Email Actions
One-click actions to generate pre-filled interview invitations or rejection emails. Streamlines communication without leaving the dashboard, saving valuable time.

### 7. 📊 Historical Analytics
Maintains specific logs of all past analyses. Includes data export capabilities (CSV), skill heatmaps, and a "Clear History" function to ensure data privacy and management.

---

## 🛠️ Technical Architecture

The project is built on a **Modular Monolith** architecture using a modern tech stack suitable for enterprise operations:

### 1. Frontend & UI: **Streamlit**
   - **Role**: The primary User Interface (UI).
   - **Why**: Delivers a beautiful, responsive, and modern web interface that integrates seamlessly with Python for fluid data visualization.

### 2. Logic & Processing: **Python 3.10**
   - **Role**: The core processing logic (The "Heart").
   - **Why**: The global standard language for AI and Data Science with extensive library support.

### 3. Data Processing: **Pandas**
   - **Role**: Tabular data management (DataFrame).
   - **Use Case**: Used to construct the "Leaderboard," rank candidates, filter by department, and prepare CSV exports.

### 4. Visualization: **Plotly**
   - **Role**: Interactive chart generation.
   - **Use Case**: Powers the bar charts in "Battle Arena" and candidate skill heatmaps.

### 5. AI & NLP Engine (The Brain):
   - **Google Gemini Pro (Generative AI)**: Acts as the "Senior HR," utilizing Direct Prompting / Full Context Injection to read resumes, summarize content, and generate questions.
   - **ReGex & Keywords (Rule-Based)**: Acts as the "High-Speed Scanner" for precise Hard Skill detection.

### 6. File Parsing: **pdfplumber & python-docx**
   - **Role**: Document translation layer.
   - **Use Case**: Extracts raw text from PDF and Word documents, converting them into a format the AI can analyze.

### 7. Database: **SQLite**
   - **Role**: Long-term Memory.
   - **Why**: A serverless, file-based database that ensures portability (runs anywhere) and local privacy (data stays on the user's machine).

---

## 🚀 How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Application**:
    ```bash
    streamlit run app.py
    ```
3.  **Access**: Open your browser at `http://localhost:8501`.

---

**Developed for**: Enterprise HR Operations & High-Volume Recruitment.
**License**: Proprietary Software.
