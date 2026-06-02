import streamlit as st
import streamlit.components.v1 as components
import pathlib

st.set_page_config(
    page_title="Core Automation — Operations Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
iframe { border: none !important; display: block; }
</style>
""", unsafe_allow_html=True)

html_path = pathlib.Path(__file__).parent / "dashboard.html"
components.html(html_path.read_text(encoding="utf-8"), height=880, scrolling=False)
