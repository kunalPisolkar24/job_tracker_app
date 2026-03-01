import streamlit as st
import polars as pl
from datetime import date
from src.config import JOBS_FILE, JOB_SCHEMA, JOB_STATUSES
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error, display_success

st.set_page_config(page_title="Job Tracker", page_icon="💼", layout="wide")
apply_custom_theme()

def main():
    st.title("Job Tracker")
    
    try:
        repo = CsvRepository(JOBS_FILE, JOB_SCHEMA)
        df = repo.get_all()
    except Exception as e:
        display_error(str(e))
        return

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
            
            if submitted:
                if not company or not title:
                    display_error("Company Name and Job Title are required.")
                else:
                    new_record = {
                        "ID": "", 
                        "Company": company,
                        "Title": title,
                        "Location": location,
                        "Status": status,
                        "Date_Applied": date_applied.isoformat(),
                        "Salary": salary,
                        "Notes": notes
                    }
                    try:
                        repo.append(new_record)
                        display_success("Application saved successfully!")
                        st.rerun()
                    except Exception as e:
                        display_error(str(e))

    st.subheader("Manage Applications")
    if not df.is_empty():
        pd_df = df.to_pandas()
        edited_df = st.data_editor(
            pd_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "ID": None, 
                "Status": st.column_config.SelectboxColumn("Status", options=JOB_STATUSES, required=True),
                "Date_Applied": st.column_config.DateColumn("Date Applied", format="YYYY-MM-DD")
            },
            key="job_editor"
        )
        
        if st.button("Save Changes to Tracker", type="primary"):
            try:
                updated_polars_df = pl.from_pandas(edited_df)
                updated_polars_df = updated_polars_df.cast(JOB_SCHEMA)
                repo.save(updated_polars_df)
                display_success("Tracker updated successfully!")
                st.rerun()
            except Exception as e:
                display_error(f"Failed to save changes: {str(e)}")
    else:
        st.info("Your job tracker is empty.")

if __name__ == "__main__":
    main()