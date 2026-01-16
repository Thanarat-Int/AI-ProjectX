import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on sys.path for local imports when running Streamlit.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.rag import answer_question, answer_question_with_employee

load_dotenv()

st.set_page_config(page_title="RAG Knowledge Assistant", layout="wide")

st.title("AI Agent")
st.caption("Enterprise knowledge assistant for internal policies and mock HR data.")

with st.sidebar:
    st.header("Settings")
    llm_provider = st.selectbox("LLM Provider", ["none", "openai", "gemini"], index=0)
    if llm_provider == "openai":
        llm_model = st.text_input("LLM Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    elif llm_provider == "gemini":
        llm_model = st.text_input("LLM Model", value=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    else:
        llm_model = st.text_input("LLM Model", value="", help="Not used in no-LLM mode")

    top_k = st.slider("Top K", min_value=1, max_value=10, value=4)
    st.caption("Free mode uses local BM25 retrieval only (no embeddings).")
    if llm_provider != "none":
        st.warning("LLM providers are disabled until ENABLE_LLM=true is set.")

employee_id = st.text_input(
    "Employee ID (for HR questions)",
    placeholder="E.g., A1001",
)
question = st.text_area(
    "Your question",
    height=140,
    placeholder="E.g., What is the incident notification window?",
)
ask_clicked = st.button("Ask")


if ask_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Thinking..."):
                if employee_id.strip():
                    data = answer_question_with_employee(
                        question=question,
                        employee_id=employee_id.strip(),
                        llm_provider=llm_provider,
                        llm_model=llm_model,
                        top_k=top_k,
                    )
                else:
                    data = answer_question(
                        question=question,
                        llm_provider=llm_provider,
                        llm_model=llm_model,
                        top_k=top_k,
                    )
            st.subheader("Answer")
            st.write(data.get("answer", ""))

        except Exception as exc:
            st.error(f"Request failed: {exc}")
