import streamlit as st
import requests, zipfile, io, os, sys, tempfile
import importlib.util

# CONFIG
GITHUB_USER = "Inumimonte"
GITHUB_REPO = "ph-degema-dashboard"
BRANCH = "main"

ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"

st.set_page_config(page_title="Launching...", layout="wide")
st.title("Loading Dashboard…")
st.info("Fetching the full application from GitHub. Please wait...")

# Download ZIP
try:
    r = requests.get(ZIP_URL, timeout=60)
    r.raise_for_status()
except Exception as e:
    st.error(f"Failed to download repository ZIP: {e}")
    st.stop()

# Extract ZIP
tmp_dir = tempfile.mkdtemp()
try:
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(tmp_dir)
except Exception as e:
    st.error(f"Failed to extract ZIP: {e}")
    st.stop()

# Locate extracted folder
root_folder = None
for name in os.listdir(tmp_dir):
    path = os.path.join(tmp_dir, name)
    if os.path.isdir(path) and name.startswith(GITHUB_REPO):
        root_folder = path
        break

if root_folder is None:
    st.error("Could not find extracted app folder.")
    st.stop()

# Add folder to sys.path
sys.path.insert(0, root_folder)

# Instead of runpy, import the real app module so Streamlit recognizes multipage structure.
spec = importlib.util.spec_from_file_location("app", os.path.join(root_folder, "app.py"))
module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(module)
except Exception as e:
    st.error(f"Error while running main app.py: {e}")
    raise
