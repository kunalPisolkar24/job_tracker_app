import plotly.express as px
import polars as pl
import streamlit as st

from src.config import JOBS_FILE, JOB_SCHEMA
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error

st.set_page_config(page_title="Job Search Analytics", page_icon="📊", layout="wide")
apply_custom_theme()


def compute_job_metrics(df: pl.DataFrame) -> dict[str, int]:
    return {
        "total": df.height,
        "interviewing": df.filter(pl.col("Status") == "Interviewing").height,
        "offers": df.filter(pl.col("Status") == "Offer").height,
        "rejected": df.filter(pl.col("Status") == "Rejected").height,
    }


def render_metrics(metrics: dict[str, int]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", metrics["total"])
    col2.metric("Interviewing", metrics["interviewing"])
    col3.metric("Offers", metrics["offers"])
    col4.metric("Rejected", metrics["rejected"])


def render_status_chart(df: pl.DataFrame) -> None:
    st.subheader("Applications by Status")
    status_counts = df.group_by("Status").len().to_pandas()
    fig = px.pie(
        status_counts,
        values="len",
        names="Status",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, width="stretch")


def render_timeline_chart(df: pl.DataFrame) -> None:
    st.subheader("Applications Over Time")

    time_df = (
        df.filter(pl.col("Date_Applied").is_not_null() & (pl.col("Date_Applied") != ""))
        .group_by("Date_Applied")
        .len()
        .sort("Date_Applied")
        .to_pandas()
    )

    if time_df.empty:
        st.info("No valid application dates found to plot.")
        return

    fig = px.line(
        time_df,
        x="Date_Applied",
        y="len",
        markers=True,
        labels={"len": "Applications", "Date_Applied": "Date"},
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, width="stretch")


def main() -> None:
    st.title("Job Search Dashboard")

    try:
        repo = CsvRepository(JOBS_FILE, JOB_SCHEMA)
        df = repo.get_all()
    except Exception as exc:
        display_error(str(exc))
        return

    if df.is_empty():
        st.info("No job applications found. Please add data in the Job Tracker.")
        return

    metrics = compute_job_metrics(df)
    render_metrics(metrics)

    st.markdown("---")
    left_col, right_col = st.columns(2)

    with left_col:
        render_status_chart(df)

    with right_col:
        render_timeline_chart(df)


if __name__ == "__main__":
    main()
