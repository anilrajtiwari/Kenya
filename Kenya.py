import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# CONFIG
# =============================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9OG1QjdPzzF2BhaSAdtSgromDYllwdTQ9GUJuGIUY-Lazh5hE_nJq-soDulleuWeJWu7xI4lGTg2v/pub?gid=0&single=true&output=csv"

st.set_page_config(
    page_title="Project Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Clean column names (very important)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

df = load_data()

# =============================
# COLUMN AUTO-DETECTION
# =============================
def find_col(keyword):
    for col in df.columns:
        if keyword in col:
            return col
    return None

status_col = find_col("status")
start_col = find_col("start")
end_col = find_col("end_date") or find_col("end")
planned_col = find_col("planned")

# =============================
# DATE CONVERSION
# =============================
for col in [start_col, end_col, planned_col]:
    if col:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# =============================
# DASHBOARD
# =============================
st.title("📊 Project Activity Dashboard")

# KPIs
c1, c2, c3 = st.columns(3)

c1.metric("Total Activities", len(df))

if status_col:
    c2.metric("Completed", (df[status_col] == "Completed").sum())
    c3.metric("Pending", (df[status_col] != "Completed").sum())
else:
    c2.metric("Completed", "N/A")
    c3.metric("Pending", "N/A")

# =============================
# STATUS PIE
# =============================
if status_col:
    st.subheader("Status Overview")
    fig1 = px.pie(df, names=status_col)
    st.plotly_chart(fig1, use_container_width=True)

# =============================
# GANTT CHART
# =============================
if start_col and end_col:
    st.subheader("Project Schedule (Gantt)")

    task_col = find_col("activity") or df.columns[0]

    fig2 = px.timeline(
        df,
        x_start=start_col,
        x_end=end_col,
        y=task_col,
        color=status_col if status_col else None
    )
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)

# =============================
# DELAY REPORT
# =============================
if planned_col and end_col:
    st.subheader("⏱ Delay Report")

    df["delay_days"] = (df[end_col] - df[planned_col]).dt.days
    st.dataframe(df[df["delay_days"] > 0])

# =============================
# RAW DATA (OPTIONAL)
# =============================
with st.expander("📄 View Raw Data"):
    st.dataframe(df)
