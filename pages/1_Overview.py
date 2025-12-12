import streamlit as st

st.set_page_config(page_title="Overview", layout="wide")
st.title("Overview")

st.markdown("""
This dashboard provides a consolidated view of nutrition and complementary feeding indicators for Degema and Port Harcourt LGAs. 
It integrates multiple data streams into a single analytical interface that enables users to filter, visualize, and interpret key findings across demographic, geographic, and programmatic dimensions.

**Key Features**
- Real-time analytics with interactive charts and tables  
- Geographic and demographic disaggregation (LGA, community, sex, age categories)  
- Summary statistics for quick program insights  
- Monitoring and evaluation sections for deeper analysis  
- Definitions & Methods section to support accurate interpretation

**How to Navigate**
1. Use the sidebar filters to refine the dataset by location, date range, or demographic characteristics.  
2. Explore the pages for Overview, Executive Summary, Methodology, Dashboard Documentation, and the main dashboard content.  
3. Select indicators of interest to view detailed visualizations and supporting metrics.  
4. Use the download options where available to export filtered datasets.
""")
