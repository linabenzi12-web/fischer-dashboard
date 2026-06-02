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
#MainMenu,footer,header,
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="stStatusWidget"],
[data-testid="stAppViewBlockContainer"] > div > div > div > div > div[data-testid="stVerticalBlock"] > div:first-child
{ display:none!important; visibility:hidden!important; height:0!important; }
.stApp { background:#070b0f!important; padding:0!important; margin:0!important; }
.block-container { padding:0!important; max-width:100%!important; margin:0!important; }
section[data-testid="stSidebar"] { display:none!important; }
iframe { border:none!important; display:block!important; margin:0!important; }
[data-testid="stVerticalBlock"] { gap:0!important; padding:0!important; }
[data-testid="stVerticalBlock"] > div { padding:0!important; margin:0!important; }
</style>
""", unsafe_allow_html=True)

html_path = pathlib.Path(__file__).parent / "dashboard.html"
components.html(html_path.read_text(encoding="utf-8"), height=920, scrolling=True)
