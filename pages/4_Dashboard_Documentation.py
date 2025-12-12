import streamlit as st

st.set_page_config(page_title="Documentation", layout="wide")
st.title("Dashboard Documentation")

st.markdown("""
Use this section as the technical and reporting annex for the dashboard.

**Contents**
- Introduction and purpose
- Objectives
- Data sources and timeframes
- Methodology and data cleaning
- Indicator definitions
- Interpretation guidance
- Limitations and recommendations

**Indicator Definitions (example)**
- MUAC categories: Green = >= 125 mm, Yellow = 115–124 mm (MAM), Red = <115 mm (SAM)
- Minimum Dietary Diversity (MDD): percentage of children 6–23 months receiving foods from 4+ food groups

**Notes**
Keep this documentation updated as methods evolve and new datasets are added.
""")
