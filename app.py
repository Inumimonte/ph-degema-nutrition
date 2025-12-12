import streamlit as st
import requests, zipfile, io, os, runpy, sys, tempfile

st.set_page_config(page_title="Nutrition Dashboard", layout="wide")

# ----------------------------
# PROFESSIONAL LOADING SCREEN
# ----------------------------
placeholder = st.empty()

with placeholder.container():
    st.markdown(
        """
        <h1 style='text-align:center; color:#0F6B3D;'>
            Nutrition & Complementary Feeding Dashboard
        </h1>

        <h3 style='text-align:center; color:#444; margin-top:-10px;'>
            Port Harcourt & Degema LGAs
        </h3>

        <p style='text-align:center; color:#666;'>
            Initializing dashboard… please wait.
        </p>

        <div style='text-align:center;'>
            <img src="https://static.streamlit.io/examples/loading.gif" width="80">
        </div>

        <p style='text-align:center; color:#888;'>
            Fetching secure application files…
        </p>

        <hr style="margin-top:20px; border:1px solid #0F6B3D;">
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------
# 1. Download repo ZIP
# ---------------------------------------------
GITHUB_USER = "Inumimonte"
GITHUB_REPO = "ph-degema-dashboard"
BRANCH = "main"

ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"

try:
    r = requests.get(ZIP_URL, timeout=60)
    r.raise_for_status()
except Exception as e:
    placeholder.error(f"Failed to download the application files: {e}")
    st.stop()

# ---------------------------------------------
# 2. Extract into temp folder
# ---------------------------------------------
tmp_dir = tempfile.mkdtemp()
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(tmp_dir)

folder = [f for f in os.listdir(tmp_dir) if f.startswith(GITHUB_REPO)][0]
root = os.path.join(tmp_dir, folder)

os.chdir(root)
sys.path.insert(0, root)

# Remove loading screen before loading real app
placeholder.empty()

# ---------------------------------------------
# 3. Run the REAL dashboard
# ---------------------------------------------
runpy.run_path(os.path.join(root, "app.py"), run_name="__main__")
