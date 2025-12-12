import streamlit as st
import requests, zipfile, io, os, runpy, sys, tempfile

# ---------------------------------------------------------
# BRANDING / UI: Professional loading screen
# ---------------------------------------------------------
st.set_page_config(page_title="Nutrition Dashboard", layout="wide")

st.markdown(
    """
    <h1 style="text-align:center; color:#007F4F; font-weight:700;">
        Nutrition & Complementary Feeding Dashboard
    </h1>
    <h3 style="text-align:center; color:#444;">
        Port Harcourt & Degema LGAs
    </h3>

    <p style="text-align:center; font-size:15px; color:#666;">
        Inumimonte David Ennis Research Work… please wait.
    </p>

    <hr style="height:4px; background-color:#1E88E5; border:none; margin-top:10px; margin-bottom:10px;" />

    <p style="text-align:center; font-size:14px; color:#555;">
        Fetching secure application files…
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# DOWNLOAD DASHBOARD ZIP FROM GITHUB
# ---------------------------------------------------------
GITHUB_USER = "Inumimonte"
GITHUB_REPO = "ph-degema-dashboard"
BRANCH = "main"

ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"

try:
    r = requests.get(ZIP_URL, timeout=60)
    r.raise_for_status()
except Exception as e:
    st.error(f"Failed to download application files: {e}")
    st.stop()

tmp_dir = tempfile.mkdtemp()
try:
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(tmp_dir)
except Exception as e:
    st.error(f"Failed to unpack application files: {e}")
    st.stop()

# Locate extracted folder
root_folder = None
for name in os.listdir(tmp_dir):
    path = os.path.join(tmp_dir, name)
    if os.path.isdir(path) and name.startswith(GITHUB_REPO):
        root_folder = path
        break

if root_folder is None:
    st.error("Unable to locate dashboard application folder.")
    st.stop()

# Run main dashboard
os.chdir(root_folder)
sys.path.insert(0, root_folder)

try:
    runpy.run_path(os.path.join(root_folder, "app.py"), run_name="__main__")
except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    raise
