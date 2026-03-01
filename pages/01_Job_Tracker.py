from datetime import date

import pandas as pd
import polars as pl
import streamlit as st

from src.config import JOBS_FILE, JOB_SCHEMA, JOB_STATUSES
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error, display_success

st.set_page_config(page_title="Job Tracker", page_icon="💼", layout="wide")
apply_custom_theme()


def build_job_record(
    company: str,
    title: str,
    location: str,
    status: str,
    date_applied: date,
    salary: str,
    notes: str,
) -> dict[str, str]:
    return {
        "ID": "",
        "Company": company.strip(),
        "Title": title.strip(),
        "Location": location.strip(),
        "Status": status,
        "Date_Applied": date_applied.isoformat(),
        "Salary": salary.strip(),
        "Notes": notes.strip(),
    }


def prepare_job_editor_dataframe(df: pl.DataFrame) -> pd.DataFrame:
    frame = df.to_pandas()
    frame["Date_Applied"] = pd.to_datetime(
        frame["Date_Applied"],
        format="%Y-%m-%d",
        errors="coerce",
    ).dt.date
    return frame


def normalize_job_editor_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized = normalized.reindex(columns=list(JOB_SCHEMA.keys()), fill_value="")
    normalized["Date_Applied"] = (
        pd.to_datetime(normalized["Date_Applied"], errors="coerce")
        .dt.strftime("%Y-%m-%d")
        .fillna("")
    )

    for column in normalized.columns:
        if column == "Date_Applied":
            continue
        normalized[column] = normalized[column].fillna("").astype(str).str.strip()

    return normalized


def save_edited_jobs(repo: CsvRepository, edited_df: pd.DataFrame) -> None:
    normalized_df = normalize_job_editor_dataframe(edited_df)
    updated_df = pl.from_pandas(normalized_df).cast(JOB_SCHEMA)
    repo.save(updated_df)


def render_add_application_form(repo: CsvRepository) -> None:
    with st.expander("➕ Add New Job Application", expanded=False):
        with st.form("add_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            company = col1.text_input("Company Name *")
            title = col2.text_input("Job Title *")

            col3, col4, col5 = st.columns(3)
            location = col3.text_input("Location")
            status = col4.selectbox("Status", JOB_STATUSES)
            date_applied = col5.date_input("Date Applied", date.today())

            salary = st.text_input("Salary / Compensation")
            notes = st.text_area("Description / Notes")

            submitted = st.form_submit_button("Save Application")

            if not submitted:
                return

            if not company.strip() or not title.strip():
                display_error("Company Name and Job Title are required.")
                return

            try:
                record = build_job_record(
                    company=company,
                    title=title,
                    location=location,
                    status=status,
                    date_applied=date_applied,
                    salary=salary,
                    notes=notes,
                )
                repo.append(record)
                display_success("Application saved successfully!")
                st.rerun()
            except Exception as exc:
                display_error(str(exc))


def render_job_editor(repo: CsvRepository, df: pl.DataFrame) -> None:
    st.subheader("Manage Applications")

    if df.is_empty():
        st.info("Your job tracker is empty.")
        return

    editable_df = prepare_job_editor_dataframe(df)
    edited_df = st.data_editor(
        editable_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "ID": None,
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=JOB_STATUSES,
                required=True,
            ),
            "Date_Applied": st.column_config.DateColumn(
                "Date Applied",
                format="YYYY-MM-DD",
            ),
        },
        key="job_editor",
    )

    if not st.button("Save Changes to Tracker", type="primary"):
        return

    try:
        save_edited_jobs(repo, edited_df)
        display_success("Tracker updated successfully!")
        st.rerun()
    except Exception as exc:
        display_error(f"Failed to save changes: {exc}")


def main() -> None:
    st.title("Job Tracker")

    try:
        repo = CsvRepository(JOBS_FILE, JOB_SCHEMA)
        df = repo.get_all()
    except Exception as exc:
        display_error(str(exc))
        return

    render_add_application_form(repo)
    render_job_editor(repo, df)


if __name__ == "__main__":
    main()
