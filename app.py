import streamlit as st
import polars as pl
import plotly.express as px
from src.config import JOBS_FILE, JOB_SCHEMA
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error

st.set_page_config(page_title="Job Search Analytics", page_icon="📊", layout="wide")
apply_custom_theme()

def main():
    st.title("Job Search Dashboard")
    
    try:
        repo = CsvRepository(JOBS_FILE, JOB_SCHEMA)
        df = repo.get_all()
    except Exception as e:
        display_error(str(e))
        return

    if df.is_empty():
        st.info("No job applications found. Please add data in the Job Tracker.")
        return

    total_apps = df.height
    interviewing = df.filter(pl.col("Status") == "Interviewing").height
    offers = df.filter(pl.col("Status") == "Offer").height
    rejected = df.filter(pl.col("Status") == "Rejected").height

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviewing", interviewing)
    col3.metric("Offers", offers)
    col4.metric("Rejected", rejected)

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Applications by Status")
        status_counts = df.group_by("Status").len().to_pandas()
        fig_status = px.pie(status_counts, values='len', names='Status', hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)
        
    with c2:
        st.subheader("Applications Over Time")
        time_df = df.filter(pl.col("Date_Applied") != "").group_by("Date_Applied").len().sort("Date_Applied").to_pandas()
        fig_time = px.line(time_df, x="Date_Applied", y="len", markers=True, 
                          labels={"len": "Applications", "Date_Applied": "Date"})
        fig_time.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_time, use_container_width=True)

if __name__ == "__main__":
    main()