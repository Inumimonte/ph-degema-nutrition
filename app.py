import streamlit as st
import requests, zipfile, io, os, runpy, sys, tempfile
from time import sleep

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Nutrition Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit menu + footer + expanders
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# PROFESSIONAL LOADING SCREEN
# ----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:60px;">
        <h1 style="color:#1B998B; font-weight:700;">Nutrition & Complementary Feeding Dashboard</h1>
        <h3 style="color:#555;">Port Harcourt & Degema LGAs</h3>
        <p style="color:#777; font-size:16px;">
            Initializing dashboard… please wait.
        </p>
        <br>
        <img src="https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/_static/img/logo.png"
             width="80" style="opacity:0.6;"/>
        <br><br>
        <div style="color:#1B998B; font-size:18px; font-weight:600;">
            Fetching secure application files…
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

progress = st.progress(0)

for i in range(1, 85):
    sleep(0.015)
    progress.progress(i)

# ----------------------------
# DOWNLOAD REAL APP FROM GITHUB
# ----------------------------
GITHUB_USER = "Inumimonte"
GITHUB_REPO = "ph-degema-dashboard"
BRANCH = "main"

ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"

try:
    r = requests.get(ZIP_URL, timeout=60)
    r.raise_for_status()
except Exception as e:
    st.error(f"Download failed: {e}")
    st.stop()

tmp_dir = tempfile.mkdtemp()
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(tmp_dir)

folder = [f for f in os.listdir(tmp_dir) if f.startswith(GITHUB_REPO)][0]
root = os.path.join(tmp_dir, folder)

os.chdir(root)
sys.path.insert(0, root)

progress.progress(100)

# ----------------------------
# RUN REAL APP
# ----------------------------
runpy.run_path(os.path.join(root, "app.py"), run_name="__main__")
