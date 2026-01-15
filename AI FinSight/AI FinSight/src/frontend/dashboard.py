import streamlit as st
import requests
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Setup Page
st.set_page_config(
    page_title="FinSight | Enterprise Analytics",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME: ENTERPRISE PURPLE & WHITE (Stable) ---
THEME = {
    "bg": "#F5F6FA",             # Soft Gray/White Background
    "sidebar": "#FFFFFF",        # White Sidebar
    "primary": "#4B1E7A",        # Deep Purple
    "secondary": "#2D9CDB",      # Cyan/Blue
    "card": "#FFFFFF",           # White Cards
    "text_h": "#2C3E50",         # Dark Navy Text
    "text_p": "#555555",         # Grey Text
    "accent": "#9B51E0",         # Lighter Purple
    "success": "#27AE60",        # Green
    "danger": "#EB5757"          # Red
}

st.markdown(f"""
<style>
    /* Global Font */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&family=Inter:wght@400;600&display=swap');

    .stApp {{
        background-color: {THEME['bg']};
        color: {THEME['text_p']};
        font-family: 'Prompt', sans-serif !important;
    }}

    /* Sidebar Styling - Formal */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0; /* Crisp border */
    }}
    
    /* Headers - Formal */
    h1, h2, h3 {{
        color: {THEME['text_h']} !important;
        font-family: 'Inter', sans-serif; /* Clean, Corporate Font */
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    
    /* Global Text */
    p, div, label {{
        font-family: 'Inter', sans-serif;
        color: {THEME['text_p']};
    }}

    /* Card Style - Corporate */
    .fi-card {{
        background-color: #FFFFFF;
        border-radius: 8px; /* Less rounded = more formal */
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); /* Very subtle shadow */
        border: 1px solid #E5E7EB;
        height: 100%;
    }}
    
    /* Metrics */
    .metric-val {{
        color: {THEME['primary']};
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        letter-spacing: -1px;
    }}
    .metric-lbl {{
        color: #6B7280;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Button Styling - Formal */
    div.stButton > button {{
        background-color: {THEME['primary']};
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        border-radius: 6px; /* Slightly squared */
        width: 100%;
        transition: 0.2s;
    }}
    div.stButton > button:hover {{
        background-color: {THEME['accent']};
        color: white;
    }}

    /* Chat Messages - Professional */
    .stChatMessage {{
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }}
       /* Input Fields - FORCE BLACK TEXT */
    input[type="text"] {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background-color: transparent !important;
    }}
    
    /* Input & Select Wrappers */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        color: #000000 !important;
    }}
    
    /* Dropdown Text Color (Selected Value) */
    div[data-baseweb="select"] span {{
        color: #000000 !important;
    }}
    
    /* Dropdown Menu POPOVER - Force White Theme */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
    }}
    
    /* Dropdown Options */
    li[role="option"],
    ul[data-baseweb="menu"] li {{
        background-color: #FFFFFF !important;
        color: #000000 !important; /* Force Black Text */
    }}
    
    /* Hover/Selected Option */
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: #F3F4F6 !important;
        color: #4B1E7A !important; /* Purple text on hover */
        font-weight: 600 !important;
    }}
    
    /* Button Styling - The Nuclear Option */
    /* Target specifically the form submit button in sidebar */
    section[data-testid="stSidebar"] button[kind="primary"], 
    section[data-testid="stSidebar"] button[kind="secondary"],
    div.stButton > button {{
        background: linear-gradient(90deg, #4B1E7A 0%, #2D9CDB 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        opacity: 1 !important;
    }}

    /* Force text color inside button */
    section[data-testid="stSidebar"] button p, 
    div.stButton > button p {{
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Hover State */
    section[data-testid="stSidebar"] button:hover,
    div.stButton > button:hover {{
        background: linear-gradient(90deg, #5D2590 0%, #38ADF0 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
        border: none !important;
    }}
    
    /* Active/Focus State */
    section[data-testid="stSidebar"] button:active, 
    section[data-testid="stSidebar"] button:focus {{
        background: #4B1E7A !important;
        color: #FFFFFF !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }}

</style>
""", unsafe_allow_html=True)
# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 🏛️ FinSight Enterprise")
    st.caption("Professional Analytics Suite")
    st.markdown("---")
    
    with st.form("main_form"):
        st.markdown("**Configuration**")
        
        # Explicit styles for text input not supported directly in st.text_input, relying on global CSS
        ticker = st.text_input("Asset Symbol", value="AAPL").upper()
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        risk = st.select_slider("Risk Profile", options=["Conservative", "Balanced", "Aggressive"], value="Balanced")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        # Added Monthly and Quarterly options as requested
        period = st.selectbox("Data Period", ["Daily (D1)", "Weekly (W1)", "Monthly (MN)", "Quarterly (Q1)"])
            
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        # Using type="primary" to help specificty
        submitted = st.form_submit_button("INITIATE ANALYSIS", type="primary")
        
    st.markdown("---")
    
    # --- CHAT WIDGET ---
    st.markdown("**Analyst Support**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "System standby."}]
    if "last_context" not in st.session_state:
        st.session_state.last_context = ""

    chat_c = st.container(height=350)
    with chat_c:
        for m in st.session_state.messages:
             with st.chat_message(m["role"]):
                st.markdown(m["content"])
                
    if q := st.chat_input("Enter query..."):
        st.session_state.messages.append({"role": "user", "content": q})
        with chat_c:
            st.chat_message("user").markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    try:
                        pl = {"query": q, "context": st.session_state.last_context}
                        r = requests.post(f"{BACKEND_URL}/chat", json=pl)
                        if r.status_code == 200:
                            ans = r.json()["response"]
                            st.markdown(ans)
                            st.session_state.messages.append({"role": "assistant", "content": ans})
                        else:
                            st.error("Service Offline")
                    except:
                        st.error("Service Offline")


# --- MAIN CONTENT ---
st.markdown(f"## Financial Intelligence Unit")
st.markdown(f"<div style='color:#6B7280; font-size: 13px; font-family: monospace;'>SESSION ID: {datetime.now().strftime('%Y%m%d-%H%M')} | STATUS: ACTIVE</div>", unsafe_allow_html=True)
st.markdown("---")

if submitted:
    st.session_state.messages = [{"role": "assistant", "content": f"Analyzing {ticker}..."}]
    
    with st.spinner("Processing Institutional Data..."):
        try:
            resp = requests.post(f"{BACKEND_URL}/analyze", json={"ticker": ticker})
            
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.last_context = data['report']
                
                # 1. METRICS ROW
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.markdown(f"""
                    <div class="fi-card">
                        <div class="metric-lbl">LAST PRICE</div>
                        <div class="metric-val">${data['current_price']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c2:
                    sig = data['signal']
                    clr = THEME['success'] if sig == "BUY" else THEME['danger']
                    st.markdown(f"""
                    <div class="fi-card">
                        <div class="metric-lbl">AI SIGNAL</div>
                        <div class="metric-val" style="color:{clr}">{sig}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c3:
                    st.markdown(f"""
                    <div class="fi-card">
                        <div class="metric-lbl">CONFIDENCE</div>
                        <div class="metric-val" style="color:{THEME['secondary']}">{data['confidence']:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c4:
                     st.markdown(f"""
                    <div class="fi-card">
                        <div class="metric-lbl">VOLATILITY</div>
                        <div class="metric-val" style="font-size: 1.5rem; color: #374151; margin-top: 5px;">MEDIUM</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 2. CHARTS & REPORT
                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
                gc1, gc2 = st.columns([2, 1])
                
                with gc1:
                    st.markdown(f"### 📈 Technical Chart: {ticker}")
                    if 'history' in data:
                        h = data['history']
                        fig = go.Figure(data=[go.Candlestick(x=h['Date'], open=h['Open'], high=h['High'], low=h['Low'], close=h['Close'])])
                        fig.update_layout(
                            template="simple_white", # CLEANEST TEMPLATE
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FFFFFF',
                            margin=dict(t=30, b=20, l=40, r=20),
                            height=500,
                            xaxis_rangeslider_visible=False,
                            xaxis=dict(showgrid=False, tickfont=dict(color='black', size=12, family='Inter')), # Black Axis Text
                            yaxis=dict(showgrid=False, tickfont=dict(color='black', size=12, family='Inter'))  # Black Axis Text
                        )
                        st.markdown('<div class="fi-card" style="padding: 15px;">', unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                with gc2:
                     st.markdown("### 📝 Analyst Memo")
                     st.markdown(f"""
                     <div class="fi-card" style="height: 520px; overflow-y: auto; background-color: #FFFFFF;">
                        <div style="border-bottom: 1px solid #E5E7EB; padding-bottom: 10px; margin-bottom: 15px;">
                            <span style="font-size: 0.8rem; color: #9CA3AF;">REPORT ID: {datetime.now().timestamp()}</span>
                        </div>
                        <div style="line-height: 1.8; color: #374151; font-size: 0.95rem; font-family: 'Inter', sans-serif;">
                            {data['report'].replace(chr(10), '<br><br>')}
                        </div>
                     </div>
                     """, unsafe_allow_html=True)

            else:
               st.error(f"Analysis Failed: {resp.text}")
               
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Backend Offline")

else:
    # Warm Welcome State - Professional
    st.markdown(f"""
    <div style='text-align: center; margin-top: 100px;'>
        <div style="display: inline-block; padding: 20px; border-radius: 50%; background-color: #F3F4F6; margin-bottom: 20px;">
            <div style='font-size: 3rem;'>🏛️</div>
        </div>
        <h2 style='color: {THEME['text_h']}; margin-bottom: 10px;'>FinSight Enterprise</h2>
        <p style='color: #6B7280;'>Authorized personnel only. Please initiate analysis from the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)
