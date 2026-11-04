import io
from datetime import date, datetime, timedelta, time
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="SGK Café | Vagtplan",page_icon="📅",layout="wide",initial_sidebar_state="collapsed")
# En ensartet lys visning på både mobil og desktop.
# Farverne er også fastlagt i .streamlit/config.toml.
st.markdown("""<style>
/* SGK Café: Enkelt lyst tema. Brug målrettede widget-regler frem for
   globale span/p-regler, så tekst og baggrund altid følges ad. */
:root {color-scheme: light !important;}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: #F8F9F7 !important;
  color: #21352B !important;
}
[data-testid="stHeader"] { background: transparent !important; }
h1, h2, h3 {color:#21352B !important;}
h1 {font-weight:750 !important; letter-spacing:-.025em;}
/* Labels: de var nærmest hvide på den lyse baggrund. */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stMarkdownContainer"] > p,
[data-testid="stTextInput"] label, [data-testid="stDateInput"] label,
[data-testid="stSelectbox"] label, [data-testid="stTimeInput"] label,
[data-testid="stTextArea"] label, [data-testid="stNumberInput"] label {
  color:#21352B !important;
  -webkit-text-fill-color:#21352B !important;
}
/* Alle lag i BaseWeb-felter – ikke kun den yderste input-wrapper. */
[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="textarea"], [data-baseweb="select"],
[data-baseweb="select"] > div,
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stDateInput"] [data-baseweb="base-input"],
[data-testid="stTimeInput"] [data-baseweb="base-input"],
[data-testid="stNumberInput"] [data-baseweb="base-input"] {
  background-color:#FFFFFF !important;
  color:#21352B !important;
  border-color:#B7C5BB !important;
}
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input,
[data-baseweb="base-input"] input,
[data-baseweb="input"] input {
  background-color:#FFFFFF !important;
  color:#21352B !important;
  -webkit-text-fill-color:#21352B !important;
  caret-color:#21352B !important;
  color-scheme:light !important;
}
input::placeholder, textarea::placeholder {
  color:#7A887E !important;
  -webkit-text-fill-color:#7A887E !important;
  opacity:1 !important;
}
/* Selectbox-værdi, datoikon, menu og kalender. */
[data-baseweb="select"] *, [data-baseweb="input"] svg,
[data-testid="stDateInput"] svg {color:#21352B !important;}
[data-baseweb="select"] svg, [data-baseweb="input"] svg {
  fill:currentColor !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="calendar"],
[role="listbox"], [role="option"], [role="dialog"] {
  background-color:#FFFFFF !important; color:#21352B !important;
}
[data-baseweb="popover"] *, [data-baseweb="menu"] *,
[data-baseweb="calendar"] *, [role="listbox"] *, [role="option"] * {
  color:#21352B !important;
}
[role="option"][aria-selected="true"] {background:#F1E5C6 !important;}
/* Segmenterede knapper skal ikke arve sort baggrund fra klienttemaet. */
[data-testid="stSegmentedControl"] button,
[data-testid="stSegmentedControl"] button *,
[data-testid="stSegmentedControl"] [role="radiogroup"] label,
[data-testid="stSegmentedControl"] [role="radiogroup"] label * {
  background-color:#FFFFFF !important;
  color:#21352B !important;
  -webkit-text-fill-color:#21352B !important;
}
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
  background-color:#F1E5C6 !important;
  border-color:#CCAD61 !important;
}
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p,
[data-testid="stTabs"] button {color:#21352B !important;}
/* Enkle knapper: standard hvide, primære guld. */
