import streamlit as st

# ---------------------------------------
#   PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Nutrition Dashboard",
    layout="wide",
)

# ---------------------------------------
#   CUSTOM GREEN HEADER (BRANDED)
# ---------------------------------------
st.markdown(
    """
    <style>
        .top-banner {
            background-color: #0D8F57;   /* Nutrition green */
            padding: 22px;
            text-align: center;
            color: white;
            border-radius: 6px;
            font-family: 'Arial', sans-serif;
            margin-bottom: 25px;
        }
        .sub-text {
            font-size: 16px;
            color: #f2f2f2;
            margin-top: -10px;
        }
    </style>

    <div class="top-banner">
        <h1>Nutrition & Complementary Feeding Dashboard</h1>
        <p class="sub-text">Port Harcourt & Degema LGAs</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------
#   HOME PAGE MESSAGE
# ---------------------------------------
st.markdown(
    """
    ## Welcome

    Use the **left sidebar** to navigate through:
    - Overview  
    - Executive Summary  
    - Methodology  
    - Dashboard Documentation  

    This home page provides a clean, branded introduction.  
    All analytics and visualizations are available inside the connected tabs.
    """
)
