import io
from datetime import date, datetime, timedelta, time
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="SGK Café | Vagtplan",page_icon="📅",layout="wide",initial_sidebar_state="collapsed")
# En ensartet lys visning på både mobil og desktop.
# Farverne er også fastlagt i .streamlit/config.toml.
st.markdown("""<style>
:root { color-scheme: light; }
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #F8F9F7 !important;
    color: #21352B !important;
}
[data-testid="stHeader"] { background: rgba(248,249,247,.95) !important; }
[data-testid="stSidebar"] { background: #F0F3EF !important; }
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] .stMarkdown,
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] {
    color: #21352B !important;
}
h1 { font-weight: 750 !important; letter-spacing: -.03em; }
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #21352B !important;
    -webkit-text-fill-color: #21352B !important;
    border: 1px solid #CBD5CD !important;
    border-radius: 10px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus {
    border-color: #B79A50 !important;
    box-shadow: 0 0 0 2px rgba(204,173,97,.25) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #77877C !important; }
[data-testid="stMetric"], [data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    border-radius: 12px;
}
[data-testid="stMetric"] {
    background: white !important; padding: 16px; border: 1px solid #E3E8E1;
}
.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
    background: #CCAD61 !important;
    border: 1px solid #B99A4E !important;
    color: #172A20 !important;
    font-weight: 700 !important;
    border-radius: 9px !important;
}
.stButton button[kind="primary"]:hover,
.stFormSubmitButton button[kind="primary"]:hover {
    background: #E0C47F !important;
    color: #172A20 !important;
}
@media (max-width: 640px) {
    .block-container { padding-top: 1.5rem; padding-left: 1rem; padding-right: 1rem; }
    h1 { font-size: 1.8rem !important; }
}
</style>""", unsafe_allow_html=True)

try:
    URL=st.secrets["SUPABASE_URL"]
    KEY=st.secrets["SUPABASE_ANON_KEY"]
except KeyError:
    st.error("Tilføj SUPABASE_URL og SUPABASE_ANON_KEY i Streamlit Secrets.")
    st.stop()

if "db" not in st.session_state:
    st.session_state.db=create_client(URL,KEY)
db=st.session_state.db

def get(table):
    return db.table(table).select("*").execute().data or []

def fail(e):
    st.error(f"Handlingen kunne ikke gennemføres: {e}")

def refresh():
    st.rerun()

def dates_of_week(day):
    monday=day-timedelta(days=day.weekday())
    return monday,monday+timedelta(days=6)

def hours(s):
    a=datetime.strptime(s["start_time"][:5],"%H:%M")
    b=datetime.strptime(s["end_time"][:5],"%H:%M")
