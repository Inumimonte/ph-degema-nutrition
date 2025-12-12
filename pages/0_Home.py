import streamlit as st
st.set_page_config(page_title="Nutrition Dashboard", layout="wide")

# ---- GREEN HEADER + WHITE BACKGROUND ----
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: white !important;
    color: black !important;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #F4F4F4 !important;
}

/* Green banner */
.top-banner {
    background-color: #0D8F57;
    padding: 22px;
    text-align: center;
    color: white;
    border-radius: 10px;
    margin-bottom: 25px;
    font-family: Arial, sans-serif;
}
.sub-text {
    color: #f0f0f0;
    font-size: 16px;
    margin-top: -8px;
}
</style>

<div class="top-banner">
    <h1>Nutrition & Complementary Feeding Dashboard</h1>
    <p class="sub-text">Port Harcourt & Degema LGAs</p>
</div>
""", unsafe_allow_html=True)


import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

# --- FORCE LIGHT BACKGROUND ---
def force_light_background():
    st.markdown(
        """
        <style>
        /* Main app background */
        .stApp {
            background-color: white !important;
            color: Green !important;
        }

        /* Main content area */
        [data-testid="stAppViewContainer"] {
            background-color: White !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F4F4F4 !important;
        }

        /* Top header */
        [data-testid="stHeader"] {
            background-color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------
# 0. DEGEMA PHC GEOJSON (MAP DATA)
# ---------------------------------------------------

degema_phc_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "ward": "Bakana 1",
                "phc": "No"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.75, 4.75], [6.76, 4.75], [6.76, 4.76], [6.75, 4.76], [6.75, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Tombia 7",
                "phc": "Yes - Model PHC Tombia"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.77, 4.75], [6.78, 4.75], [6.78, 4.76], [6.77, 4.76], [6.77, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Degema I 11",
                "phc": "Yes - Degema Comprehensive PHC"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.79, 4.75], [6.80, 4.75], [6.80, 4.76], [6.79, 4.76], [6.79, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Usokun-Degema 13",
                "phc": "Yes - PHC Usokun-Degema"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.81, 4.75], [6.82, 4.75], [6.82, 4.76], [6.81, 4.76], [6.81, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Obuama 14",
                "phc": "Yes - Model PHC Obu-ama"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.83, 4.75], [6.84, 4.75], [6.84, 4.76], [6.83, 4.76], [6.83, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Bukuma 15",
                "phc": "Yes - PHC Bukuma"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.85, 4.75], [6.86, 4.75], [6.86, 4.76], [6.85, 4.76], [6.85, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Bille 16",
                "phc": "Yes - PHC Bille"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.87, 4.75], [6.88, 4.75], [6.88, 4.76], [6.87, 4.76], [6.87, 4.75]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "ward": "Ke/Old Bakana 17",
                "phc": "Yes - PHC Ke"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[6.89, 4.75], [6.90, 4.75], [6.90, 4.76], [6.89, 4.76], [6.89, 4.75]]]
            }
        }
    ]
}

# ---------------------------------------------------
# 1. THEME & HELPER FUNCTIONS
# ---------------------------------------------------

# Colour theme (Orange + neutrals)
PRIMARY_COLOR = "#FF9933"   # navy
SECONDARY_COLOR = "#1B998B" # teal
ACCENT_COLOR = "#F4B400"    # amber
LIGHT_GREY = "#F4F4F4"

# MUAC category colours (health-intuitive)
MUAC_COLORS = {
    "Normal": "#2E8B57",                       # green
    "Moderate acute malnutrition": "#FF9933",  # orange
    "Severe acute malnutrition": "#CC3300",    # red
    "Unknown": "#999999",
}

# LGA colours
LGA_COLORS = {
    "Degema": PRIMARY_COLOR,
    "Port Harcourt": SECONDARY_COLOR,
}

def dedup_columns(cols):
    """Ensure column names are unique by adding .1, .2 etc. to duplicates."""
    new_cols = []
    seen = {}
    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}.{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    return new_cols


def parse_float_from_str(value):
    """Extract numeric value from strings like '14  cm', '12.5cm' etc."""
    if pd.isna(value):
        return np.nan
    s = str(value)
    m = re.search(r"(\d+\.?\d*)", s)
    if not m:
        return np.nan
    return float(m.group(1))


def classify_muac(muac_cm):
    """Create MUAC category from MUAC in cm."""
    if pd.isna(muac_cm):
        return "Unknown"
    if muac_cm < 11.5:
        return "Severe acute malnutrition"
    elif muac_cm < 12.5:
        return "Moderate acute malnutrition"
    else:
        return "Normal"


def cf_age_is_correct(value):
    """Return True if 'Age to Start CF' is 6 months, else False/NaN."""
    if pd.isna(value):
        return np.nan
    s = str(value)
    m = re.search(r"(\d+)", s)
    if not m:
        return np.nan
    return int(m.group(1)) == 6


def compute_diet_diversity(row, diet_cols):
    """
    Diet diversity score = count of food groups consumed.
    Any non-empty / non-'No' value counts as 1.
    """
    score = 0
    for c in diet_cols:
        val = row.get(c)
        if pd.isna(val):
            continue
        s = str(val).strip().lower()
        if s and s not in ["no", "0", "none", "nan"]:
            score += 1
    return score


def clean_yes_no(series):
    """Standardise Yes/No variables."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": "Yes", "no": "No"})
    )


def clean_age_introduced_cf(series):
    """
    Standardise 'Age Introduced CF' into bands: <4, 4–6, 6–8, 8–11, 12+ months.
    Falls back to original text if pattern not recognised.
    """
    s = series.astype(str).str.strip().str.lower()
    result = []
    for v in s:
        if "less than 4" in v or "<4" in v:
            result.append("<4 months")
        elif "4-6" in v or "4 - 6" in v:
            result.append("4–6 months")
        elif "6-8" in v or "6 - 8" in v or ">6 months -8 months" in v:
            result.append("6–8 months")
        elif "8-11" in v or "8 -11" in v or ">8 months -11 months" in v:
            result.append("8–11 months")
        elif "12" in v:
            result.append("12+ months")
        elif v == "nan":
            result.append("")
        else:
            result.append(v)
    return pd.Series(result)


def build_meal_summary(df):
    """Create a small MEAL indicator table from the filtered data."""
    n = len(df)
    rows = []

    def add(domain, indicator, value, numerator=None, denominator=None, unit="%"):
        rows.append(
            {
                "Domain": domain,
                "Indicator": indicator,
                "Value": value,
                "Numerator": numerator,
                "Denominator": denominator,
                "Unit": unit,
            }
        )

    if n == 0:
        return pd.DataFrame(rows)

    # --- Monitoring ---
    add("Monitoring", "Children assessed", n, numerator=n, unit="count")

    comms = df["community_clean"].replace("", np.nan).nunique()
    add("Monitoring", "Communities covered", comms, numerator=comms, unit="count")

    if "heard_cf" in df.columns:
        p = (df["heard_cf"] == "Yes").mean()
        add(
            "Monitoring",
            "Caregivers who have heard of CF",
            f"{p*100:.1f}",
            numerator=int(round(p * n)),
            denominator=n,
            unit="%",
        )

    # --- Evaluation ---
    if "muac_category" in df.columns:
        muac_counts = df["muac_category"].value_counts()
        total_muac = muac_counts.sum()
        if total_muac > 0:
            for cat in ["Normal", "Moderate acute malnutrition", "Severe acute malnutrition"]:
                c = muac_counts.get(cat, 0)
                p = c / total_muac
                add(
                    "Evaluation",
                    f"Children with {cat}",
                    f"{p*100:.1f}",
                    numerator=int(c),
                    denominator=int(total_muac),
                    unit="%",
                )

    # --- Accountability ---
    if "cf_info_source" in df.columns:
        p_hcw = (df["cf_info_source"] == "Health Care Workers").mean()
        add(
            "Accountability",
            "Caregivers whose main CF info source is health care workers",
            f"{p_hcw*100:.1f}",
            numerator=int(round(p_hcw * n)),
            denominator=n,
            unit="%",
        )

    if "visit_freq_clean" in df.columns:
        p_reg = df["visit_freq_clean"].isin(["Weekly", "Monthly"]).mean()
        add(
            "Accountability",
            "Caregivers visiting facility weekly/monthly for nutrition advice",
            f"{p_reg*100:.1f}",
            numerator=int(round(p_reg * n)),
            denominator=n,
            unit="%",
        )

    # --- Learning ---
    if "cf_knowledge_correct" in df.columns:
        valid = df["cf_knowledge_correct"].notna()
        if valid.any():
            p_k = df.loc[valid, "cf_knowledge_correct"].mean()
            add(
                "Learning",
                "Caregivers with correct knowledge (start CF at 6 months)",
                f"{p_k*100:.1f}",
                numerator=int(round(p_k * valid.sum())),
                denominator=int(valid.sum()),
                unit="%",
            )

    if "cf_practice_timely" in df.columns:
        valid = df["cf_practice_timely"].notna()
        if valid.any():
            p_p = df.loc[valid, "cf_practice_timely"].mean()
            add(
                "Learning",
                "Children introduced to CF at 6–8 months",
                f"{p_p*100:.1f}",
                numerator=int(round(p_p * valid.sum())),
                denominator=int(valid.sum()),
                unit="%",
            )

    return pd.DataFrame(rows)


def compute_missingness(df, cols, group_col=None):
    """
    Returns missingness percentages for selected columns.
    If group_col is provided (e.g., LGA), returns missingness per group.
    """
    results = []

    if group_col is None:
        for c in cols:
            if c not in df.columns:
                continue
            missing = df[c].isna().mean()
            results.append({"Indicator": c, "Missing (%)": round(missing * 100, 1)})
        return pd.DataFrame(results)

    if group_col not in df.columns:
        return pd.DataFrame(results)

    groups = df[group_col].dropna().unique()
    for g in groups:
        df_g = df[df[group_col] == g]
        for c in cols:
            if c not in df_g.columns:
                continue
            missing = df_g[c].isna().mean()
            results.append({
                group_col: g,
                "Indicator": c,
                "Missing (%)": round(missing * 100, 1)
            })
    return pd.DataFrame(results)


def detect_outliers_iqr(series):
    """Return a boolean Series: True where the value is an outlier based on IQR rule."""
    s = pd.to_numeric(series, errors="coerce")
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return pd.Series([False] * len(s), index=s.index)
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (s < lower) | (s > upper)


def build_consistency_issues(df):
    """
    Build a table of logical consistency issues.
    """
    issues = []

    n = len(df)
    if n == 0:
        return pd.DataFrame(columns=["Issue", "Count", "Example rule"])

    # 1. Knowledge–practice gap
    if "cf_knowledge_correct" in df.columns and "cf_practice_timely" in df.columns:
        mask_gap = (df["cf_knowledge_correct"] == True) & (df["cf_practice_timely"] == False)
        count_gap = int(mask_gap.sum())
        if count_gap > 0:
            issues.append({
                "Issue": "Knowledge–practice gap",
                "Count": count_gap,
                "Example rule": "Caregiver knows to start CF at 6 months but did not introduce CF at 6–8 months"
            })

    # 2. MUAC numeric present but category 'Unknown'
    if "muac_cm" in df.columns and "muac_category" in df.columns:
        mask_miss_cat = df["muac_cm"].notna() & df["muac_category"].eq("Unknown")
        cnt = int(mask_miss_cat.sum())
        if cnt > 0:
            issues.append({
                "Issue": "MUAC category missing despite numeric MUAC",
                "Count": cnt,
                "Example rule": "muac_cm not null but muac_category = 'Unknown'"
            })

        # 3. MUAC category not Unknown but MUAC numeric missing
        mask_miss_muac = df["muac_cm"].isna() & ~df["muac_category"].eq("Unknown")
        cnt2 = int(mask_miss_muac.sum())
        if cnt2 > 0:
            issues.append({
                "Issue": "MUAC category filled but numeric MUAC missing",
                "Count": cnt2,
                "Example rule": "muac_cm is null but muac_category is 'Normal'/'MAM'/'SAM'"
            })

    return pd.DataFrame(issues)


def find_duplicates(df):
    """
    Try to detect potential duplicate records.
    If no explicit ID, use composite of key fields.
    """
    for id_col in ["Child ID", "Child_ID", "child_id", "Unique ID", "unique_id"]:
        if id_col in df.columns:
            dup_mask = df[id_col].duplicated(keep=False) & df[id_col].notna()
            dups = df[dup_mask].copy()
            dups["Duplicate key"] = df[id_col]
            return dups

    composite_cols = [
        "lga_clean",
        "community_clean",
        "child_sex",
        "age_introduced_cf_cat",
        "muac_cm",
    ]
    use_cols = [c for c in composite_cols if c in df.columns]
    if not use_cols:
        return pd.DataFrame()

    dup_mask = df.duplicated(subset=use_cols, keep=False)
    dups = df[dup_mask].copy()
    dups["Duplicate key"] = dups[use_cols].astype(str).agg("|".join, axis=1)
    return dups


def compute_group_quality_scores(df, indicators, group_col):
    """
    Compute a simple data quality score per group.
    Score = 100 - avg missing%.
    """
    results = []

    if group_col not in df.columns:
        return pd.DataFrame()

    groups = df[group_col].dropna().unique()
    for g in groups:
        df_g = df[df[group_col] == g]
        if df_g.empty:
            continue

        missing_vals = []
        for c in indicators:
            if c not in df_g.columns:
                continue
            m = df_g[c].isna().mean() * 100
            missing_vals.append(m)

        if not missing_vals:
            continue

        avg_missing = float(np.mean(missing_vals))
        score = 100.0 - avg_missing

        if score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        else:
            grade = "C"

        results.append({
            group_col: g,
            "Avg missing (%)": round(avg_missing, 1),
            "Data quality score": round(score, 1),
            "Grade": grade,
        })

    if not results:
        return pd.DataFrame()

    df_scores = pd.DataFrame(results).sort_values("Data quality score", ascending=False)
    return df_scores


# ---------------------------------------------------
# 2. DATA LOADING & TRANSFORMATION
# ---------------------------------------------------

@st.cache_data
def load_data():
    # Degema
    degema = pd.read_excel("DEGEMA_DATA_NEW.xlsx")
    degema.columns = dedup_columns(degema.columns)
    if "LGA" not in degema.columns:
        degema["LGA"] = "Degema"

    # Port Harcourt
    ph_raw = pd.read_excel("PORT HARCOURT_DATA_MOH_Book1.xlsx")
    header = ph_raw.iloc[0]
    ph = ph_raw[1:].copy()
    ph.columns = dedup_columns(header)
    if "LGA" not in ph.columns:
        ph["LGA"] = "Port Harcourt"

    df = pd.concat([degema, ph], ignore_index=True)

    df["lga_clean"] = df["LGA"].astype(str).str.strip().str.title()
    df = df[df["lga_clean"].isin(["Degema", "Port Harcourt"])]

    if "Name of community" in df.columns:
        df["community_clean"] = df["Name of community"].astype(str).str.strip().str.title()
    else:
        df["community_clean"] = ""

    if "Residence" in df.columns:
        df["residence_clean"] = df["Residence"].astype(str).str.strip().str.title()
    else:
        df["residence_clean"] = ""

    if "Sex.1" in df.columns:
        df["child_sex"] = df["Sex.1"].astype(str).str.strip().str.title()
    else:
        df["child_sex"] = ""

    if "Highest Educational Level" in df.columns:
        df["cg_education"] = (
            df["Highest Educational Level"].astype(str).str.strip().str.title()
        )
    else:
        df["cg_education"] = ""

    if "Heard of CF" in df.columns:
        df["heard_cf"] = clean_yes_no(df["Heard of CF"])
    else:
        df["heard_cf"] = np.nan

    if "Age to Start CF" in df.columns:
        df["cf_knowledge_correct"] = df["Age to Start CF"].apply(cf_age_is_correct)
    else:
        df["cf_knowledge_correct"] = np.nan

    if "Age Introduced CF" in df.columns:
        df["age_introduced_cf_cat"] = clean_age_introduced_cf(df["Age Introduced CF"])
        df["cf_practice_timely"] = df["age_introduced_cf_cat"].eq("6–8 months")
    else:
        df["age_introduced_cf_cat"] = ""
        df["cf_practice_timely"] = np.nan

    if "Meals Per Day" in df.columns:
        meals = df["Meals Per Day"].astype(str).str.strip().str.lower()
        meals = meals.replace(
            {
                "1-2 times": "1–2 times",
                "1 - 2 times": "1–2 times",
                "2-3 times": "2–3 times",
                "3-4 times": "3–4 times",
                "3 - 4 times": "3–4 times",
                "5 or more times": "5 or more times",
                "5- more times": "5 or more times",
            }
        )
        df["meals_per_day_cat"] = meals.replace("nan", "")
    else:
        df["meals_per_day_cat"] = ""

    if "Variety of Foods" in df.columns:
        df["variety_foods"] = clean_yes_no(df["Variety of Foods"])
    else:
        df["variety_foods"] = np.nan

    if "Fortified Foods Use" in df.columns:
        df["fortified_food_use"] = (
            df["Fortified Foods Use"].astype(str).str.strip().str.title()
        )
    else:
        df["fortified_food_use"] = ""

    if "Visit Frequency" in df.columns:
        df["visit_freq_clean"] = df["Visit Frequency"].astype(str).str.strip().str.title()
    else:
        df["visit_freq_clean"] = ""

    if "Mean MUAC (cm)" in df.columns:
        df["muac_cm"] = df["Mean MUAC (cm)"].apply(parse_float_from_str)
        df["muac_category"] = df["muac_cm"].apply(classify_muac)
    else:
        df["muac_cm"] = np.nan
        df["muac_category"] = "Unknown"

    diet_cols = [
        "Breast milk",
        "Grains, roots, tubers",
        "Legumes, nuts",
        "Dairy products",
        "Flesh foods",
        "Eggs",
        "Vitamin A-rich fruits/veg",
        "Other fruits/veg",
    ]
    for c in diet_cols:
        if c not in df.columns:
            df[c] = np.nan
    df["diet_diversity"] = df.apply(lambda row: compute_diet_diversity(row, diet_cols), axis=1)

    if "Source of CF Info.1" in df.columns:
        src = df["Source of CF Info.1"].astype(str).str.strip().str.lower()
        src = src.replace(
            {
                "healthcare workers": "health care workers",
                "healthcare worker": "health care workers",
                "health care workers ": "health care workers",
                "health care": "health care workers",
                "family members ": "family members",
                "community leader ": "community leaders",
            }
        )
        df["cf_info_source"] = src.replace("nan", "").str.title()
    else:
        df["cf_info_source"] = ""

    if "Visible Severe Wasting" in df.columns:
        df["visible_wasting"] = clean_yes_no(df["Visible Severe Wasting"])
    else:
        df["visible_wasting"] = np.nan

    if "Oedema" in df.columns:
        df["oedema"] = clean_yes_no(df["Oedema"])
    else:
        df["oedema"] = np.nan

    return df


df = load_data()

# ---------------------------------------------------
# 3. SIDEBAR FILTERS + DOWNLOADS
# ---------------------------------------------------

st.sidebar.title("Filters")

def add_multiselect_filter(label, col_name, df_current):
    if col_name not in df_current.columns:
        return df_current
    options = sorted(
        [x for x in df_current[col_name].dropna().unique() if str(x).strip() != ""]
    )
    if not options:
        return df_current
    selected = st.sidebar.multiselect(label, options, default=options)
    if selected and len(selected) < len(options):
        df_current = df_current[df_current[col_name].isin(selected)]
    return df_current

filtered = df.copy()
filtered = add_multiselect_filter("LGA", "lga_clean", filtered)
filtered = add_multiselect_filter("Community", "community_clean", filtered)
filtered = add_multiselect_filter("Residence", "residence_clean", filtered)
filtered = add_multiselect_filter("Child sex", "child_sex", filtered)
filtered = add_multiselect_filter("Caregiver education", "cg_education", filtered)
filtered = add_multiselect_filter("Age introduced to CF", "age_introduced_cf_cat", filtered)
filtered = add_multiselect_filter("Meals per day", "meals_per_day_cat", filtered)
filtered = add_multiselect_filter("MUAC category", "muac_category", filtered)
filtered = add_multiselect_filter("Visit frequency (nutrition advice)", "visit_freq_clean", filtered)

meal_summary = build_meal_summary(filtered)

csv_filtered = filtered.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Download filtered data (CSV)",
    data=csv_filtered,
    file_name="filtered_nutrition_data.csv",
    mime="text/csv",
)

csv_meal = meal_summary.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Download MEAL summary (CSV)",
    data=csv_meal,
    file_name="meal_summary.csv",
    mime="text/csv",
)

# ---------------------------------------------------
# 4. HEADER & TABS
# ---------------------------------------------------

# Header with (placeholder) logo + project title
logo_col, title_col = st.columns([1, 4])
with logo_col:
    # To use a real logo, save e.g. 'logo_afdb.png' in the app folder and uncomment:
    # st.image("logo_afdb.png", use_column_width=True)
    st.markdown("**Project partners:** AfDB / Africa CDC")

with title_col:
    st.markdown(
        f"""
        <h2 style="margin-bottom:0; color:{PRIMARY_COLOR};">
        Degema &amp; Port Harcourt Self Research on Nutrition Surveillance &amp; Complementary Feeding Dashboard
        </h2>
        <p style="color:#555555; margin-top:0.25rem;">
        Internal MEAL dashboard – NGO project performance view
        </p>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
Use the filters on the left to focus on specific LGAs, communities, or child groups.
Tabs below follow the MEAL structure plus data quality and documentation.
"""
)

tab_intro, tab_overview, tab_exec, tab_mon, tab_eval, tab_acc, tab_learn, tab_quality, tab_meta = st.tabs(
    ["Introduction", "Overview", "Executive Summary", "Monitoring", "Evaluation", "Accountability", "Learning", "Data Quality", "Definitions & Methods"]
)

with tab_intro:
    st.header("Introduction")
    st.markdown("""
    ## Purpose of the Dashboard
    This dashboard provides an integrated platform for monitoring, analysing, and visualizing nutrition and complementary feeding indicators across Degema and Port Harcourt LGAs. It transforms raw field data into actionable insights that support planning, decision-making, and performance improvement. By presenting real-time trends, disaggregated performance metrics, and community-level insights, the dashboard enables stakeholders to track progress, identify gaps, and prioritize high-need locations for targeted interventions.

    ## Who It Is Designed For
    This dashboard is intended for:
    - Nutrition and Health Programme Managers  
    - MEAL Specialists  
    - Government health authorities at State, LGA, and Ward levels  
    - Donor agencies and implementing partners  
    - Field supervisors and community health workers  
    - Researchers and policy planners  

    It supports both high-level strategic planning and detailed operational decision-making.

    ## Summary of Data Collection
    Data used in this dashboard originates from structured nutrition and complementary feeding assessments carried out in Degema and Port Harcourt. Trained field workers collected standardized data using digital tools to ensure accuracy and consistency. The dataset includes:
    - Anthropometric indicators (e.g., MUAC)  
    - Infant and Young Child Feeding (IYCF) metrics  
    - Complementary feeding practices  
    - Household demographic and contextual information  

    Data cleaning, validation, and harmonization steps were completed prior to dashboard integration to ensure high-quality, reliable analytics.

    ## How to Interpret the Results
    When using this dashboard:
    - Apply filters such as LGA, community, and date range to focus the analysis.  
    - Review indicators together (e.g., MUAC vs feeding practices) for a complete nutritional profile.  
    - Prioritize trends and patterns over single data points, especially where sample sizes vary.  
    - Consider local factors such as access to services, cultural feeding practices, and seasonality.  
    - Take note of any missing values or anomalies that may influence interpretation.  

    The dashboard is a decision-support tool designed to complement field findings, supervision data, and contextual knowledge for program planning and resource allocation.
    """)




# ---------------------------------------------------
# EXECUTIVE SUMMARY TAB
# ---------------------------------------------------

with tab_exec:
    st.subheader("Executive Summary")

    total_children = len(filtered)
    total_communities = filtered["community_clean"].replace("", np.nan).nunique()
    muac_counts = filtered["muac_category"].value_counts()
    total_muac = muac_counts.sum()
    sev = muac_counts.get("Severe acute malnutrition", 0)
    mod = muac_counts.get("Moderate acute malnutrition", 0)
    normal = muac_counts.get("Normal", 0)

    if total_muac > 0:
        sev_prop = sev / total_muac
        mod_prop = mod / total_muac
        normal_prop = normal / total_muac
    else:
        sev_prop = mod_prop = normal_prop = np.nan

    if "cf_practice_timely" in filtered.columns and total_children > 0:
        valid_p = filtered["cf_practice_timely"].notna()
        timely_cf_prop = (
            filtered.loc[valid_p, "cf_practice_timely"].mean()
            if valid_p.any()
            else np.nan
        )
    else:
        timely_cf_prop = np.nan

    if "cf_knowledge_correct" in filtered.columns and total_children > 0:
        valid_k = filtered["cf_knowledge_correct"].notna()
        correct_k_prop = (
            filtered.loc[valid_k, "cf_knowledge_correct"].mean()
            if valid_k.any()
            else np.nan
        )
    else:
        correct_k_prop = np.nan

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Children assessed", f"{total_children}")
    col2.metric("Communities covered", f"{total_communities}")
    if not np.isnan(sev_prop):
        col3.metric("Severe acute malnutrition", f"{sev_prop:.1%}")
    if not np.isnan(timely_cf_prop):
        col4.metric("Children with timely CF (6–8 months)", f"{timely_cf_prop:.1%}")

    st.markdown(
        """
        **Quick interpretation**

        - *Coverage*: How many children and communities are represented in the current filters.  
        - *Nutritional status*: Severe and moderate acute malnutrition (SAM/MAM) are based on MUAC.  
        - *Practices*: Timely complementary feeding (CF) means CF started between **6–8 months**.  
        - *Knowledge*: Correct CF knowledge means caregiver identifies **6 months** as the time to start CF.
        """
    )

    # LGA comparison: MUAC categories
    muac_lga = (
        filtered.groupby(["lga_clean", "muac_category"])
        .size()
        .reset_index(name="Children")
    )
    if not muac_lga.empty:
        fig_muac_lga = px.bar(
            muac_lga,
            x="lga_clean",
            y="Children",
            color="muac_category",
            barmode="relative",
            title="MUAC categories by LGA (current filters)",
            labels={"lga_clean": "LGA"},
            color_discrete_map=MUAC_COLORS,
        )
        st.plotly_chart(fig_muac_lga, use_container_width=True)

    # CF knowledge vs practice high-level view
    if "cf_knowledge_correct" in filtered.columns and "cf_practice_timely" in filtered.columns:
        kpi_df = pd.DataFrame(
            {
                "Indicator": ["Correct CF knowledge", "Timely CF practice (6–8 months)"],
                "Value": [
                    correct_k_prop * 100 if not np.isnan(correct_k_prop) else np.nan,
                    timely_cf_prop * 100 if not np.isnan(timely_cf_prop) else np.nan,
                ],
            }
        )
        kpi_df = kpi_df.dropna()
        if not kpi_df.empty:
            fig_k = px.bar(
                kpi_df,
                x="Indicator",
                y="Value",
                title="Knowledge and practice of complementary feeding",
                labels={"Value": "Percentage (%)"},
                text="Value",
            )
            fig_k.update_traces(texttemplate="%{text:.1f}")
            fig_k.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_k, use_container_width=True)

    st.markdown("### MEAL summary (for current filters)")
    if not meal_summary.empty:
        st.dataframe(meal_summary)
    else:
        st.info("No data available for the current filters.")

# ---------------------------------------------------
# MONITORING TAB (INCLUDES MAP)
# ---------------------------------------------------

with tab_mon:
    st.subheader("Monitoring: Coverage, Screening & Service Availability")

    total_children = len(filtered)
    total_communities = filtered["community_clean"].replace("", np.nan).nunique()

    heard_cf_prop = (
        (filtered["heard_cf"] == "Yes").mean()
        if "heard_cf" in filtered.columns and total_children > 0
        else np.nan
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Children assessed", f"{total_children}")
    col2.metric("Communities covered", f"{total_communities}")
    if not np.isnan(heard_cf_prop):
        col3.metric("Caregivers who have heard of CF", f"{heard_cf_prop:.1%}")

    # Children by LGA
    lga_counts = (
        filtered.groupby("lga_clean")
        .size()
        .reset_index(name="Children")
    )
    if not lga_counts.empty:
        fig_lga = px.bar(
            lga_counts,
            x="lga_clean",
            y="Children",
            title="Children assessed by LGA",
            labels={"lga_clean": "LGA"},
            color="lga_clean",
            color_discrete_map=LGA_COLORS,
        )
        st.plotly_chart(fig_lga, use_container_width=True)

    # Children by community (top 20)
    comm_counts = (
        filtered.groupby("community_clean")
        .size()
        .reset_index(name="Children")
        .sort_values("Children", ascending=False)
    )
    if not comm_counts.empty:
        fig_comm = px.bar(
            comm_counts.head(20),
            x="community_clean",
            y="Children",
            title="Children assessed by community (top 20)",
            labels={"community_clean": "Community"},
        )
        st.plotly_chart(fig_comm, use_container_width=True)

    st.markdown(
        """
        **Note:** Coverage indicators reflect the number of children and communities captured
        in the Degema and Port Harcourt surveys under the current filters.
        """
    )

    # -------- Degema PHC MAP (from GeoJSON) --------
    st.markdown("### Service availability map – Degema PHC")
    # After the green banner:
   st.markdown("### Degema PHC Service Availability Map")
   st.pydeck_chart(r)


    poly_rows = []
    for feat in degema_phc_geojson["features"]:
        coords = feat["geometry"]["coordinates"][0]  # outer ring
        ward = feat["properties"]["ward"]
        phc = feat["properties"]["phc"]
        poly_rows.append(
            {
                "ward": ward,
                "phc": phc,
                "coordinates": coords,
            }
        )

    poly_df = pd.DataFrame(poly_rows)

    all_lons = [pt[0] for poly in poly_df["coordinates"] for pt in poly]
    all_lats = [pt[1] for poly in poly_df["coordinates"] for pt in poly]
    center_lon = float(np.mean(all_lons))
    center_lat = float(np.mean(all_lats))

    def phc_color(phc_str):
        if isinstance(phc_str, str) and phc_str.strip().lower().startswith("yes"):
            return [0, 128, 0, 140]  # greenish
        else:
            return [200, 200, 200, 80]  # grey

    poly_df["fill_color"] = poly_df["phc"].apply(phc_color)

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=poly_df,
        get_polygon="coordinates",
        get_fill_color="fill_color",
        get_line_color=[0, 0, 0],
        stroked=True,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=0,
        bearing=0,
    )

    r = pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        tooltip={"text": "{ward}\n{phc}"},
        map_style="light",
    )

    st.pydeck_chart(r)

# ---------------------------------------------------
# EVALUATION TAB
# ---------------------------------------------------

with tab_eval:
    st.subheader("Evaluation: Nutritional Status & Outcomes")

    muac_counts = filtered["muac_category"].value_counts(dropna=False)
    total_muac = muac_counts.sum()

    if total_muac > 0:
        normal = muac_counts.get("Normal", 0)
        mod = muac_counts.get("Moderate acute malnutrition", 0)
        sev = muac_counts.get("Severe acute malnutrition", 0)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Normal MUAC", f"{normal / total_muac:.1%}")
        col2.metric("Moderate acute malnutrition", f"{mod / total_muac:.1%}")
        col3.metric("Severe acute malnutrition", f"{sev / total_muac:.1%}")
        col4.metric(
            "Mean MUAC (cm)",
            f"{filtered['muac_cm'].mean():.2f}"
            if not filtered["muac_cm"].dropna().empty
            else "N/A",
        )

        muac_df = pd.DataFrame({
            "MUAC category": muac_counts.index.astype(str),
            "Children": muac_counts.values
        })
        fig_muac = px.bar(
            muac_df,
            x="MUAC category",
            y="Children",
            title="MUAC categories",
            labels={"Children": "Children"},
            color="MUAC category",
            color_discrete_map=MUAC_COLORS,
        )
        st.plotly_chart(fig_muac, use_container_width=True)

    muac_lga = (
        filtered.groupby(["lga_clean", "muac_category"])
        .size()
        .reset_index(name="Children")
    )
    if not muac_lga.empty:
        fig_muac_lga = px.bar(
            muac_lga,
            x="lga_clean",
            y="Children",
            color="muac_category",
            barmode="stack",
            title="MUAC categories by LGA",
            labels={"lga_clean": "LGA"},
            color_discrete_map=MUAC_COLORS,
        )
        st.plotly_chart(fig_muac_lga, use_container_width=True)

    muac_box = filtered.dropna(subset=["muac_cm"])
    if not muac_box.empty:
        fig_muac_box = px.box(
            muac_box,
            x="lga_clean",
            y="muac_cm",
            title="Distribution of MUAC (cm) by LGA",
            labels={"lga_clean": "LGA", "muac_cm": "MUAC (cm)"},
            color="lga_clean",
            color_discrete_map=LGA_COLORS,
        )
        st.plotly_chart(fig_muac_box, use_container_width=True)

    for col, title in [
        ("visible_wasting", "Visible severe wasting"),
        ("oedema", "Oedema (pitting oedema of both feet)"),
    ]:
        if col in filtered.columns:
            vc = filtered[col].value_counts(dropna=False)
            if vc.empty:
                continue
            counts = pd.DataFrame({
                "Category": vc.index.astype(str),
                "Children": vc.values
            })
            fig = px.bar(
                counts,
                x="Category",
                y="Children",
                title=title,
                labels={"Category": title, "Children": "Children"},
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        **Interpretation tip:** MUAC and visible wasting/oedema provide complementary views of
        acute malnutrition. Use this tab to identify LGAs or communities that may require
        targeted outreach or supply support.
        """
    )

# ---------------------------------------------------
# ACCOUNTABILITY TAB
# ---------------------------------------------------

with tab_acc:
    st.subheader("Accountability: Information Sources & Service Use")

    n = len(filtered)
    prop_from_hcws = (
        (filtered["cf_info_source"] == "Health Care Workers").mean()
        if n > 0
        else np.nan
    )
    prop_monthly_or_weekly = (
        filtered["visit_freq_clean"].isin(["Weekly", "Monthly"]).mean()
        if n > 0
        else np.nan
    )

    col1, col2 = st.columns(2)
    if not np.isnan(prop_from_hcws):
        col1.metric(
            "CF info from health workers",
            f"{prop_from_hcws:.1%}",
        )
    if not np.isnan(prop_monthly_or_weekly):
        col2.metric(
            "Caregivers visiting facility weekly/monthly",
            f"{prop_monthly_or_weekly:.1%}",
        )

    src = filtered["cf_info_source"]
    src = src[src != ""]
    if not src.empty:
        vc = src.value_counts(dropna=False)
        info_counts = pd.DataFrame({
            "Source": vc.index.astype(str),
            "Caregivers": vc.values
        })
        fig_info = px.bar(
            info_counts,
            x="Source",
            y="Caregivers",
            title="Source of information on complementary feeding",
            labels={"Source": "Source of CF Info", "Caregivers": "Caregivers"},
        )
        st.plotly_chart(fig_info, use_container_width=True)

    freq = filtered["visit_freq_clean"]
    freq = freq[freq != ""]
    if not freq.empty:
        vc = freq.value_counts(dropna=False)
        freq_counts = pd.DataFrame({
            "Category": vc.index.astype(str),
            "Caregivers": vc.values
        })
        fig_freq = px.bar(
            freq_counts,
            x="Category",
            y="Caregivers",
            title="Frequency of visiting a health facility for nutrition advice",
            labels={"Category": "Visit Frequency", "Caregivers": "Caregivers"},
        )
        st.plotly_chart(fig_freq, use_container_width=True)

    var = filtered["variety_foods"].dropna()
    if not var.empty:
        vc = var.value_counts(dropna=False)
        var_counts = pd.DataFrame({
            "Category": vc.index.astype(str),
            "Caregivers": vc.values
        })
        fig_var = px.bar(
            var_counts,
            x="Category",
            y="Caregivers",
            title="Caregivers offering a variety of foods to the child",
            labels={"Category": "Variety of foods", "Caregivers": "Caregivers"},
        )
        st.plotly_chart(fig_var, use_container_width=True)

    st.markdown(
        """
        **Use this tab to:**  
        - Track whether caregivers are receiving information from formal health workers vs. informal sources.  
        - Monitor how often caregivers actually present to facilities for nutrition advice.
        """
    )

# ---------------------------------------------------
# LEARNING TAB
# ---------------------------------------------------

with tab_learn:
    st.subheader("Learning: What drives better nutrition outcomes?")

    n = len(filtered)
    if "cf_knowledge_correct" in filtered.columns and n > 0:
        valid_k = filtered["cf_knowledge_correct"].notna()
        prop_knowledge_correct = (
            filtered.loc[valid_k, "cf_knowledge_correct"].mean()
            if valid_k.any()
            else np.nan
        )
    else:
        prop_knowledge_correct = np.nan

    if "cf_practice_timely" in filtered.columns and n > 0:
        valid_p = filtered["cf_practice_timely"].notna()
        prop_practice_timely = (
            filtered.loc[valid_p, "cf_practice_timely"].mean()
            if valid_p.any()
            else np.nan
        )
    else:
        prop_practice_timely = np.nan

    col1, col2 = st.columns(2)
    if not np.isnan(prop_knowledge_correct):
        col1.metric(
            "Caregivers with correct knowledge (start CF at 6 months)",
            f"{prop_knowledge_correct:.1%}",
        )
    if not np.isnan(prop_practice_timely):
        col2.metric(
            "Children introduced to CF at 6–8 months",
            f"{prop_practice_timely:.1%}",
        )

    edu_muac = (
        filtered.dropna(subset=["cg_education", "muac_category"])
        .groupby(["cg_education", "muac_category"])
        .size()
        .reset_index(name="Children")
    )
    if not edu_muac.empty:
        fig_edu_muac = px.bar(
            edu_muac,
            x="cg_education",
            y="Children",
            color="muac_category",
            barmode="relative",
            title="MUAC category by caregiver education level",
            labels={"cg_education": "Caregiver education"},
            color_discrete_map=MUAC_COLORS,
        )
        st.plotly_chart(fig_edu_muac, use_container_width=True)

    if "cf_knowledge_correct" in filtered.columns:
        cf_muac = (
            filtered.dropna(subset=["cf_knowledge_correct", "muac_category"])
            .groupby(["cf_knowledge_correct", "muac_category"])
            .size()
            .reset_index(name="Children")
        )
        if not cf_muac.empty:
            cf_muac["cf_knowledge_correct"] = cf_muac["cf_knowledge_correct"].map(
                {True: "Correct (6 months)", False: "Incorrect"}
            )
            fig_cf_muac = px.bar(
                cf_muac,
                x="cf_knowledge_correct",
                y="Children",
                color="muac_category",
                barmode="relative",
                title="MUAC category vs correct knowledge of CF start age",
                labels={"cf_knowledge_correct": "Knowledge of age to start CF"},
                color_discrete_map=MUAC_COLORS,
            )
            st.plotly_chart(fig_cf_muac, use_container_width=True)

    dd_muac = filtered.dropna(subset=["diet_diversity", "muac_category"])
    if not dd_muac.empty:
        fig_dd = px.box(
            dd_muac,
            x="muac_category",
            y="diet_diversity",
            title="Diet diversity score by MUAC category",
            labels={"muac_category": "MUAC category", "diet_diversity": "Diet diversity score"},
            color="muac_category",
            color_discrete_map=MUAC_COLORS,
        )
        st.plotly_chart(fig_dd, use_container_width=True)

    st.markdown(
        """
        **Learning questions you can explore here:**
        - Do caregivers with higher education or correct CF knowledge have better child MUAC?  
        - Are higher diet diversity scores associated with lower acute malnutrition?  
        - Use the filters to focus on specific LGAs or communities.
        """
    )

# ---------------------------------------------------
# DATA QUALITY TAB
# ---------------------------------------------------

with tab_quality:
    st.subheader("Data Quality: Missingness, Outliers, Consistency & Scorecard")

    indicators = [
        "muac_cm",
        "muac_category",
        "age_introduced_cf_cat",
        "cf_practice_timely",
        "cf_knowledge_correct",
        "visit_freq_clean",
        "meals_per_day_cat",
        "variety_foods",
        "cf_info_source",
        "diet_diversity",
    ]

    st.markdown("### 1. Missingness by indicator")
    overall_missing = compute_missingness(filtered, indicators)
    st.markdown("**Overall missingness (%)**")
    st.dataframe(overall_missing)

    if not overall_missing.empty:
        fig_overall = px.bar(
            overall_missing,
            x="Indicator",
            y="Missing (%)",
            title="Missingness by Indicator (Overall)",
            text="Missing (%)",
        )
        fig_overall.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_overall, use_container_width=True)

    st.markdown("**Missingness by LGA (%)**")
    missing_lga = compute_missingness(filtered, indicators, group_col="lga_clean")
    st.dataframe(missing_lga)

    if not missing_lga.empty:
        fig_lga = px.bar(
            missing_lga,
            x="Indicator",
            y="Missing (%)",
            color="lga_clean",
            barmode="group",
            title="Missingness by LGA and indicator",
            text="Missing (%)",
            color_discrete_map=LGA_COLORS,
        )
        fig_lga.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_lga, use_container_width=True)

    st.markdown("### 2. Outliers in numeric indicators")

    outlier_rows = []

    if "muac_cm" in filtered.columns:
        muac_out = detect_outliers_iqr(filtered["muac_cm"])
        n_out = int(muac_out.sum())
        st.markdown(f"- **MUAC (cm)** outliers: `{n_out}` record(s) flagged by IQR rule.")
        if n_out > 0:
            outlier_rows.append(
                filtered.loc[muac_out, ["lga_clean", "community_clean", "muac_cm"]]
                .assign(Indicator="MUAC (cm)")
            )
            fig_muac_out = px.box(
                filtered,
                x="lga_clean",
                y="muac_cm",
                points="all",
                title="MUAC (cm) distribution with potential outliers",
                color="lga_clean",
                color_discrete_map=LGA_COLORS,
            )
            st.plotly_chart(fig_muac_out, use_container_width=True)

    if "diet_diversity" in filtered.columns:
        dd_out = detect_outliers_iqr(filtered["diet_diversity"])
        n_dd_out = int(dd_out.sum())
        st.markdown(f"- **Diet diversity score** outliers: `{n_dd_out}` record(s) flagged.")
        if n_dd_out > 0:
            outlier_rows.append(
                filtered.loc[dd_out, ["lga_clean", "community_clean", "diet_diversity"]]
                .assign(Indicator="Diet diversity")
            )
            fig_dd_out = px.box(
                filtered,
                x="lga_clean",
                y="diet_diversity",
                points="all",
                title="Diet diversity distribution with potential outliers",
                color="lga_clean",
                color_discrete_map=LGA_COLORS,
            )
            st.plotly_chart(fig_dd_out, use_container_width=True)

    if outlier_rows:
        st.markdown("**Details of potential outliers (subset of fields)**")
        outlier_table = pd.concat(outlier_rows, ignore_index=True)
        st.dataframe(outlier_table)
        csv_outliers = outlier_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download outlier records (CSV)",
            csv_outliers,
            "outliers_records.csv",
            "text/csv",
        )
    else:
        st.info("No numeric outliers detected based on the IQR rule (for the selected filters).")

    st.markdown("### 3. Logical consistency issues")
    issues_df = build_consistency_issues(filtered)
    if not issues_df.empty:
        st.dataframe(issues_df)
        csv_issues = issues_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download consistency issues (CSV)",
            csv_issues,
            "consistency_issues.csv",
            "text/csv",
        )
    else:
        st.info("No logical consistency issues found based on the current checks.")

    st.markdown("### 4. Potential duplicate records")
    dups = find_duplicates(filtered)
    if not dups.empty:
        st.markdown(
            "The table below shows records that share the same ID or the same combination "
            "of key fields (LGA, community, child sex, age introduced CF, MUAC cm)."
        )
        show_cols = [c for c in [
            "Duplicate key",
            "lga_clean",
            "community_clean",
            "child_sex",
            "age_introduced_cf_cat",
            "muac_cm",
            "cf_info_source",
        ] if c in dups.columns]
        st.dataframe(dups[show_cols])

        csv_dups = dups.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download potential duplicates (CSV)",
            csv_dups,
            "potential_duplicates.csv",
            "text/csv",
        )
    else:
        st.info("No potential duplicate records detected using the current rules.")

    st.markdown("### 5. Data Quality Scorecard (by area)")
    st.markdown(
        "Score = 100 − average % missing across key indicators.\n\n"
        "- **A**: ≥85 (high data quality)\n"
        "- **B**: 70–84.9 (moderate)\n"
        "- **C**: <70 (needs attention)\n"
    )

    level = st.radio(
        "Choose level for ranking:",
        ["LGA", "Community", "Facility"],
        index=0,
        horizontal=True,
    )

    dq_indicators = indicators

    if level == "LGA":
        group_col = "lga_clean"
    elif level == "Community":
        group_col = "community_clean"
    else:
        facility_col = None
        for cand in ["Facility", "Health Facility", "Health facility", "Facility Name"]:
            if cand in filtered.columns:
                facility_col = cand
                break
        if facility_col is None:
            st.info(
                "No facility column found (e.g. 'Facility' or 'Health Facility'). "
                "Adjust the code if your facility column has a different name."
            )
            group_col = None
        else:
            group_col = facility_col

    if group_col is not None:
        dq_scores = compute_group_quality_scores(filtered, dq_indicators, group_col)
        if dq_scores.empty:
            st.info("No data quality scores could be computed for this level.")
        else:
            st.markdown(f"**Data quality scorecard by {level}**")
            st.dataframe(dq_scores)

            fig_score = px.bar(
                dq_scores,
                x=group_col,
                y="Data quality score",
                color="Grade",
                title=f"Data Quality Score by {level}",
                labels={group_col: level, "Data quality score": "Score (0–100)"},
                text="Grade",
            )
            fig_score.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 100])
            st.plotly_chart(fig_score, use_container_width=True)

            csv_scores = dq_scores.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"📥 Download {level} data quality scorecard (CSV)",
                csv_scores,
                f"data_quality_scorecard_{level.lower()}.csv",
                "text/csv",
            )

# ---------------------------------------------------
# DEFINITIONS & METHODS TAB
# ---------------------------------------------------

with tab_meta:
    st.subheader("Definitions & Methods")

    st.markdown(
        """
        This tab documents how key indicators are defined and calculated in the dashboard.
        It is intended to support transparent MEAL reporting and reproducibility.
        """
    )

    st.markdown("### Data sources")
    st.markdown(
        """
        - **Degema LGA**: Child nutrition and complementary feeding survey data (PHC/Community-based).  
        - **Port Harcourt LGA**: Child nutrition and complementary feeding survey data.  
        - Each row represents **one child–caregiver pair** assessed during the survey exercise.
        """
    )

    st.markdown("### Key variables")
    st.markdown(
        """
        - **LGA (`lga_clean`)** – Degema or Port Harcourt, standardised to title case.  
        - **Community (`community_clean`)** – Name of community as recorded in the survey, cleaned for spelling/case.  
        - **Residence (`residence_clean`)** – Urban/rural or other categories, depending on the questionnaire.  
        - **Child sex (`child_sex`)** – Sex of the child (Male/Female).  
        - **Caregiver education (`cg_education`)** – Highest educational level attained by the caregiver.
        """
    )

    st.markdown("### Nutritional status")
    st.markdown(
        """
        **MUAC (Mid-Upper Arm Circumference)**  
        - `muac_cm` – Numeric MUAC in centimetres, extracted from the free-text field *Mean MUAC (cm)*.  
        - `muac_category` – Derived from `muac_cm` using standard cut-offs:  
          - **Severe acute malnutrition (SAM)**: MUAC < 11.5 cm  
          - **Moderate acute malnutrition (MAM)**: 11.5 ≤ MUAC < 12.5 cm  
          - **Normal**: MUAC ≥ 12.5 cm  
          - **Unknown**: MUAC missing or could not be parsed from the raw field.  

        **Visible wasting & oedema**  
        - `visible_wasting` – Yes/No, based on clinical observation of severe wasting.  
        - `oedema` – Yes/No, presence of bilateral pitting oedema of the feet.
        """
    )

    st.markdown("### Complementary feeding (CF) knowledge & practices")
    st.markdown(
        """
        - **Heard of CF (`heard_cf`)** – Caregiver has heard the term *complementary feeding* (Yes/No).  
        - **Correct CF knowledge (`cf_knowledge_correct`)** – `True` if caregiver states **6 months** as the correct age to start CF.  
        - **Age Introduced CF (`age_introduced_cf_cat`)** – Age band at which CF was actually started:  
          - <4 months, 4–6 months, 6–8 months, 8–11 months, 12+ months, or other recorded values.  
        - **Timely CF practice (`cf_practice_timely`)** – `True` if CF was introduced at **6–8 months** (aligned with IYCF guidance).  
        - **Meals per day (`meals_per_day_cat`)** – Number of meals per day, grouped into categories such as 1–2, 2–3, 3–4, 5+ times.  
        - **Variety of foods (`variety_foods`)** – Yes/No, whether child is given a variety of foods.  
        - **Fortified foods use (`fortified_food_use`)** – Categorical description of fortified foods used (if any).
        """
    )

    st.markdown("### Diet diversity")
    st.markdown(
        """
        The **diet diversity score (`diet_diversity`)** is calculated as the number of food groups consumed,
        across the following groups (1 point each if consumed):  

        1. Breast milk  
        2. Grains, roots, tubers  
        3. Legumes, nuts  
        4. Dairy products  
        5. Flesh foods (meat, fish, poultry)  
        6. Eggs  
        7. Vitamin A-rich fruits and vegetables  
        8. Other fruits and vegetables  

        Any non-empty, non-'No' response in each group is counted as 1.
        """
    )

    st.markdown("### Accountability & service use")
    st.markdown(
        """
        - **CF information source (`cf_info_source`)** – Main source of CF information as reported by caregiver  
          (e.g. Health Care Workers, family members, community leaders).  
        - **Visit frequency (`visit_freq_clean`)** – Reported frequency of visiting a health facility for nutrition advice  
          (e.g. Weekly, Monthly, Occasionally, Rarely, Never).  
        - Indicators in the Accountability tab summarise:  
          - Proportion of caregivers whose main CF information source is **health workers**.  
          - Proportion of caregivers visiting a facility **weekly or monthly** for nutrition advice.
        """
    )

    st.markdown("### Data quality metrics & scorecard")
    st.markdown(
        """
        - **Missingness** – Percentage of records where a given field is blank or NA.  
        - **Outliers** – Identified using the Interquartile Range (IQR) rule for numeric fields like MUAC and diet diversity.  
        - **Consistency issues** – Flags contradictions such as:
          - Correct knowledge (start CF at 6 months) but CF not introduced at 6–8 months.  
          - MUAC numeric present but MUAC category missing (or vice versa).  
        - **Duplicate records** – Either repeated IDs (if available) or repeated combinations of key fields.  

        **Data Quality Scorecard**  
        - For each LGA / community / facility:  
          - Compute the average percentage of missing data across key indicators.  
          - **Data quality score = 100 − (average % missing)**.  
          - Grades:  
            - **A**: score ≥ 85 (high data quality)  
            - **B**: 70–84.9 (moderate data quality)  
            - **C**: < 70 (requires attention)
        """
    )

    st.markdown(
        """
        If you adapt this dashboard for other LGAs or surveys, update this tab so that users can quickly
        understand how indicators are derived and how to interpret the visualisations.
        """
    )




