import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================
# CONFIG
# =============================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9OG1QjdPzzF2BhaSAdtSgromDYllwdTQ9GUJuGIUY-Lazh5hE_nJq-soDulleuWeJWu7xI4lGTg2v/pub?gid=0&single=true&output=csv"

st.set_page_config(
    page_title="Project Progress Monitoring Dashboard",
    layout="wide"
)

# ==================================================
# DATA LOADING
# ==================================================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

df = load_data()

# ==================================================
# REFRESH CONTROL
# ==================================================
st.sidebar.title("Controls")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    f"Last refreshed: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}"
)

# ==================================================
# COLUMN AUTO-DETECTION
# ==================================================
def find_col(keyword):
    for col in df.columns:
        if keyword in col:
            return col
    return None

activity_col = find_col("activity") or df.columns[0]
status_col   = find_col("status")
start_col    = find_col("start")
end_col      = find_col("end_date") or find_col("end")
planned_col  = find_col("planned")
owner_col    = find_col("owner")

# ==================================================
# DATE CONVERSION
# ==================================================
for col in [start_col, end_col, planned_col]:
    if col:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ==================================================
# HEADER
# ==================================================
st.title("Project Progress Monitoring Dashboard")
st.markdown(
    """
    **Objective:**  
    To provide a centralized, real-time view of project activities,
    progress status, schedule performance, and delay analysis.
    """
)

st.divider()

# ==================================================
# EXECUTIVE SUMMARY
# ==================================================
st.subheader("Executive Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Activities", len(df))

if status_col:
    c2.metric("Completed", (df[status_col] == "Completed").sum())
    c3.metric("In Progress", (df[status_col] == "In Progress").sum())
    c4.metric("Not Started", (df[status_col] == "Not Started").sum())
else:
    c2.metric("Completed", "N/A")
    c3.metric("In Progress", "N/A")
    c4.metric("Not Started", "N/A")

st.divider()

# ==================================================
# STATUS DISTRIBUTION
# ==================================================
if status_col:
    st.subheader("Activity Status Distribution")

    fig_status = px.pie(
        df,
        names=status_col,
        title="Distribution of Activities by Status"
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# ==================================================
# PROJECT SCHEDULE (GANTT)
# ==================================================
if start_col and end_col:
    st.subheader("Project Schedule Overview")

    fig_gantt = px.timeline(
        df,
        x_start=start_col,
        x_end=end_col,
        y=activity_col,
        color=status_col if status_col else None,
        hover_data=[owner_col] if owner_col else None
    )

    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Activities"
    )

    st.plotly_chart(fig_gantt, use_container_width=True)

st.divider()

# ==================================================
# DELAY ANALYSIS
# ==================================================
if planned_col and end_col:
    st.subheader("Schedule Delay Analysis")

    df["delay_days"] = (df[end_col] - df[planned_col]).dt.days
    delayed_df = df[df["delay_days"] > 0]

    if len(delayed_df) > 0:
        st.markdown(
            "The following activities have exceeded their planned completion dates:"
        )
        st.dataframe(
            delayed_df[
                [activity_col, owner_col, planned_col, end_col, "delay_days"]
            ] if owner_col else delayed_df
        )
    else:
        st.success("No delayed activities at this time.")

st.divider()

# ==================================================
# DETAILED REGISTER
# ==================================================
with st.expander("Detailed Activity Register"):
    st.dataframe(df)

# ==================================================
# FOOTER
# ==================================================
st.markdown(
    """
    ---
    **Note:**  
    This dashboard is automatically generated from a centrally maintained
    project activity register. Users are advised to refresh data after updates
    to ensure the latest information is displayed.
    """
)
