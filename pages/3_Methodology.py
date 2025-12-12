import streamlit as st

st.set_page_config(page_title="Methodology", layout="wide")
st.title("Methodology")

st.markdown("""
## Study Design & Data Sources
Data are derived from structured nutrition assessments conducted across Degema and Port Harcourt LGAs, following national and international measurement standards. Sources include:
- MUAC measurements (6–59 months)
- Household demographic questionnaires
- IYCF modules and complementary feeding practices

## Data Collection Procedures
- Trained enumerators collected data using digital tools.
- Supervisors performed spot checks and validation.
- Data were uploaded daily and subject to quality control.

## Data Cleaning & QA
- Duplicate removal and handling of missing values.
- Standardisation of location names, validation of MUAC ranges, and outlier checks.
- Documented cleaning steps are reproducible and applied prior to analysis.

## Analysis
Descriptive statistics and trend visualizations are used to summarize indicators. Indicator definitions follow WHO/UNICEF guidance.
""")
