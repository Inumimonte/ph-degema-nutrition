import streamlit as st

st.set_page_config(page_title="Executive Summary", layout="wide")
st.title("Executive Summary")

st.markdown("""
### Background
Malnutrition remains a critical public health challenge affecting children under five. This dashboard presents findings from nutrition and complementary feeding assessments conducted in Degema and Port Harcourt LGAs.

### Key Findings
- **Screening Coverage:** summary of number of children assessed and screening completeness.
- **Nutritional Status:** overview of MUAC classifications and prevalence of MAM/SAM.
- **IYCF & Feeding Practices:** trends in exclusive breastfeeding, meal frequency, and dietary diversity.
- **Community-Level Insights:** identification of high-risk communities for targeted support.
- **Trends and Patterns:** notable increases/decreases across reporting periods.

### Program Implications
- Prioritize communities with elevated malnutrition rates.  
- Strengthen caregiver education and community outreach.  
- Improve service delivery coverage during outreach campaigns.  
- Use the dashboard for evidence-driven resource allocation.

### Conclusion
The dashboard supports continuous surveillance and data-driven decision-making to improve child nutrition outcomes.
""")
