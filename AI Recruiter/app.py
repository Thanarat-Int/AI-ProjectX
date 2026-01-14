import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.parser import parse_resume
from src.analyzer import get_analyzer
from src.db import init_db, save_analysis, get_history
from src.report import generate_pdf_report
from src.file_manager import save_uploaded_file

# --- Page Config ---
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 PRO DESIGN SYSTEM (World-Class UI) ---
st.markdown("""
<style>
    /* 1. Global Reset & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #0f172a; /* Slate 900 */
        background-color: #f8fafc; /* Slate 50 */
    }

    /* 2. Container & Layout */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
        max-width: 1200px;
    }

    /* 3. Typography */
    h1, h2, h3 {
        color: #1e293b; /* Slate 800 */
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    h1 { font-size: 2.25rem; margin-bottom: 1rem; }
    h2 { font-size: 1.5rem; margin-bottom: 0.75rem; }
    h3 { font-size: 1.25rem; margin-bottom: 0.5rem; }

    /* 4. Sidebar Modernization */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 24px -12px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    /* 5. Card Component (Glassmorphism Lite) */
    .stCard, div[data-testid="stMetric"], div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e2e8f0; /* Slate 200 */
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stCard:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }

    /* 6. Upload Area (Premium Dropzone) */
    [data-testid="stFileUploader"] {
        background-color: #f8fafc; /* Slate 50 */
        border: 2px dashed #3b82f6; /* Blue 500 */
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        transition: background-color 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        background-color: #eff6ff; /* Blue 50 */
    }

    /* 7. Inputs & Text Areas */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 12px;
        color: #1e293b;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* 8. Buttons (Gradient & Action) */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    }

    /* 9. Metrics & Highlights */
    [data-testid="stMetricLabel"] {
        color: #64748b; /* Slate 500 */
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    [data-testid="stMetricValue"] {
        color: #0f172a; /* Slate 900 */
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricDelta"] {
        color: #16a34a; /* Green 600 */
    }

    /* 10. DataFrames & Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 11. Custom Accents */
    .success-box {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 16px;
        border-radius: 8px;
        color: #166534;
        margin-bottom: 1rem;
    }
    
    .info-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 16px;
        border-radius: 8px;
        color: #1e40af;
        margin-bottom: 1rem;
    }

</style>
""", unsafe_allow_html=True)

# ... imports
from src.db import init_db, save_analysis, get_history, clear_history # Added clear_history

# ... (Previous code remains)

def main():
    # Sidebar
    with st.sidebar:
        st.title("🟦 AI Recruiter")
        st.markdown("**Intelligent Screening System**")
        
        st.markdown("---")
        st.header("Navigation")
        page = st.radio("Menu", ["Analysis Dashboard", "Compare Candidates", "History Logs"], label_visibility="collapsed")
        
        st.markdown("---")
        st.header("⚙️ Settings")
        ai_engine = st.selectbox(
            "Engine Model", 
            ["Rule-Based (Basic)", "Gemini LLM (Advanced)"],
            index=0 
        )
        
        st.markdown("---")
        is_blind = st.checkbox("🕶️ Blind Hiring Mode", value=False)
        
        # --- NEW: Department Presets to help HR ---
        if page == "Analysis Dashboard":
            st.markdown("---")
            st.header("🎯 Position Context")
            
            # 1. Department
            dept = st.selectbox("Department", ["Custom / General", "Software Engineering", "Sales & Marketing", "Finance & Accounting", "Human Resources"])
            
            # 2. Seniority Level (NEW)
            seniority = st.selectbox("Seniority Level", ["Intern / Junior", "Mid-Level / Officer", "Senior / Lead", "Manager / Director", "C-Level / Executive"])
            
            # Logic to build Preset Skills
            base_skills = []
            
            # Department Keywords
            if dept == "Software Engineering":
                base_skills = ["Python", "SQL", "React", "Cloud", "Git"]
            elif dept == "Sales & Marketing":
                base_skills = ["Communication", "Negotiation", "CRM", "Social Media", "Salesforce"]
            elif dept == "Finance & Accounting":
                base_skills = ["Excel", "SAP", "Financial Analysis", "Forecasting", "Auditing"]
            elif dept == "Human Resources":
                base_skills = ["Recruitment", "Labor Law", "Communication", "Empathy", "Conflict Resolution"]
            
            # Seniority Keywords (Additive)
            level_skills = []
            if "Senior" in seniority or "Lead" in seniority:
                level_skills = ["Leadership", "Mentoring", "System Design", "Problem Solving"]
            elif "Manager" in seniority or "Director" in seniority:
                level_skills = ["Team Management", "Strategy", "Budgeting", "Hiring", "Planning"]
            elif "C-Level" in seniority:
                level_skills = ["Vision", "Business Strategy", "Execution", "Stakeholder Management", "Scale"]
            elif "Intern" in seniority:
                level_skills = ["Learning", "Adaptability", "Research"]
            
            # Combine
            final_preset_str = ", ".join(base_skills + level_skills)

    # Routing
    if page == "Analysis Dashboard":
        show_analysis_page(ai_engine, is_blind, final_preset_str) # Pass combined preset
    elif page == "Compare Candidates":
        show_comparison_page(is_blind)
    elif page == "History Logs":
        show_history_page(is_blind)

def show_analysis_page(engine_choice, is_blind, preset_skills):
    st.markdown("## 🚀 Analysis Dashboard")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.info("ℹ️ **Job Context criteria**")
        uploaded_jd = st.text_area("Job Description", height=200, placeholder="Paste JD here...", label_visibility="collapsed")
        
        with st.expander("Target Specific Skills?", expanded=True):
             # Use the preset as default value
             essential_skills_input = st.text_input("Essential Skills (Auto-filled)", value=preset_skills, placeholder="e.g. Python, SQL")
             essential_skills = [s.strip() for s in essential_skills_input.split(',')] if essential_skills_input else []

    # ... (Rest of show_analysis_page matches previous, just ensure indentation)
    with col2:
        st.success("📂 **Candidate Resumes**")
        uploaded_resumes = st.file_uploader(
            "Drag & Drop PDFs here", 
            type=["pdf", "docx"], 
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        analyze_btn = st.button("Start Analysis ⚡", type="primary", use_container_width=True)

    # --- RESULTS SECTION (Full Width) ---
    if analyze_btn:
        st.divider()
        process_analysis(uploaded_resumes, uploaded_jd, engine_choice, essential_skills, is_blind)

# ... (process_analysis and show_comparison_page remain unchanged) ...

def show_history_page(is_blind):
    st.markdown("## 📜 Historical Logs")
    history = get_history()
    
    if history:
        # Layout: Table on top, Action button below
        df = pd.DataFrame(history, columns=["ID", "Timestamp", "Filename", "Score", "Skills"])
        if is_blind:
             df['Filename'] = [f"Candidate #{i+1}" for i in range(len(df))]
        
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "history.csv", "text/csv")
        
        with col2:
            # Dangerous action protected by a check
            if st.button("🗑️ Clear All History", type="secondary"):
                clear_history()
                st.rerun()
    else:
        st.info("Empty history.")


def process_analysis(uploaded_resumes, uploaded_jd, engine_choice, essential_skills, is_blind):
    if not uploaded_resumes or not uploaded_jd:
        st.error("Please provide both Job Description and Resumes.")
        return

    results = []
    progress_bar = st.progress(0)
    
    total_files = len(uploaded_resumes)
    
    for idx, uploaded_file in enumerate(uploaded_resumes):
        # 1. Save
        file_path = save_uploaded_file(uploaded_file)
        
        # 2. Parse
        resume_text = parse_resume(uploaded_file)
        if not resume_text:
            continue 

        # 3. Analyze
        engine_key = "Gemini LLM" if "Gemini" in engine_choice else "Rule-Based"
        analyzer = get_analyzer(engine_key)
        
        analysis_result = analyzer.analyze(resume_text, uploaded_jd, essential_skills)
        
        # 4. Process Result
        try:
            if "```json" in analysis_result:
                json_str = analysis_result.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_result:
                json_str = analysis_result.split("```")[1].strip()
            else:
                json_str = analysis_result
            
            data = json.loads(json_str)
            save_analysis(uploaded_file.name, data, file_path)
            
            results.append({
                "Name": uploaded_file.name,
                "Score": data.get('match_score', 0),
                "Level": data.get('seniority', 'N/A'), # Added seniority
                "Skills": data.get('key_skills', []),
                "Missing": data.get('missing_skills', []),
                "Summary": data.get('candidate_summary', ''),
                "Questions": data.get('interview_questions', [])
            })
            
        except Exception as e:
            print(f"Error: {e}")
        
        progress_bar.progress((idx + 1) / total_files)

    st.balloons()
    
    if results:
        st.divider()
        st.subheader("🏆 Live Leaderboard")
        
        df = pd.DataFrame(results)
        df = df.sort_values(by="Score", ascending=False)
        
        if is_blind:
            df['Name'] = [f"Candidate #{i+1}" for i in range(len(df))]

        # Display Table with column configuration
        df_display = df.copy()
        df_display['Skills'] = df_display['Skills'].apply(lambda x: ", ".join(x))
        df_display['Missing'] = df_display['Missing'].apply(lambda x: ", ".join(x))
        
        st.dataframe(
            df_display[['Name', 'Score', 'Skills', 'Missing']].style.background_gradient(subset=['Score'], cmap='Blues'),
            use_container_width=True
        )

def show_comparison_page(is_blind):
    st.markdown("## ⚔️ Candidate Battle Arena")
    
    history = get_history()
    if not history:
        st.warning("No data found. Please analyze resumes first.")
        return
        
    df = pd.DataFrame(history, columns=["ID", "Timestamp", "Filename", "Score", "Skills"])
    
    # Smart Selection Logic: Auto-select top 2 distinct candidates if available
    default_ix1, default_ix2 = 0, 0
    if len(df) > 1:
        default_ix2 = 1

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔵 Fighter 1")
        f1 = st.selectbox("Select Candidate", df['Filename'], index=default_ix1, key="f1")
    with col2:
        st.markdown("### 🔴 Fighter 2")
        f2 = st.selectbox("Select Candidate", df['Filename'], index=default_ix2, key="f2")

    if f1 and f2:
        d1 = df[df['Filename'] == f1].iloc[0]
        d2 = df[df['Filename'] == f2].iloc[0]
        
        n1 = f1 if not is_blind else "Candidate A"
        n2 = f2 if not is_blind else "Candidate B"
        
        # Visual Comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=[n1, n2],
            x=[d1['Score'], d2['Score']],
            orientation='h',
            marker=dict(color=['#2563eb', '#ef4444']),
            text=[f"{d1['Score']}%", f"{d2['Score']}%"],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Match Score Comparison",
            xaxis_title="Score (%)",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Winner Declaration
        if d1['Score'] > d2['Score']:
            st.success(f"🏆 WINNER: **{n1}** (+{d1['Score'] - d2['Score']}%)")
        elif d2['Score'] > d1['Score']:
            st.success(f"🏆 WINNER: **{n2}** (+{d2['Score'] - d1['Score']}%)")
        else:
            st.info("⚖️ DRAW: Exact Match!")

def show_history_page(is_blind):
    st.markdown("## 📜 Historical Logs")
    history = get_history()
    
    if history:
        df = pd.DataFrame(history, columns=["ID", "Timestamp", "Filename", "Score", "Skills"])
        if is_blind:
             df['Filename'] = [f"Candidate #{i+1}" for i in range(len(df))]
        
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "history.csv", "text/csv")
            
        with col2:
            if st.button("🗑️ Clear All History"):
                clear_history()
                st.rerun()
    else:
        st.info("Empty history.")

if __name__ == "__main__":
    main()
