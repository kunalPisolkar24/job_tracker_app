import streamlit as st
import polars as pl
from src.config import CONTACTS_FILE, CONTACT_SCHEMA
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error, display_success

st.set_page_config(page_title="Network Contacts", page_icon="🤝", layout="wide")
apply_custom_theme()

def main():
    st.title("Network & Referrals")

    try:
        repo = CsvRepository(CONTACTS_FILE, CONTACT_SCHEMA)
        df = repo.get_all()
    except Exception as e:
        display_error(str(e))
        return

    with st.expander("➕ Add New Contact", expanded=False):
        with st.form("add_contact_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Name *")
            company = col2.text_input("Company *")
            
            col3, col4 = st.columns(2)
            email = col3.text_input("Email")
            phone = col4.text_input("Phone Number")
            
            linkedin = st.text_input("LinkedIn URL")
            notes = st.text_area("Relationship / Notes")
            
            submitted = st.form_submit_button("Save Contact")
            
            if submitted:
                if not name or not company:
                    display_error("Name and Company are required.")
                else:
                    new_record = {
                        "ID": "", 
                        "Name": name,
                        "Company": company,
                        "Email": email,
                        "Phone": phone,
                        "LinkedIn": linkedin,
                        "Notes": notes
                    }
                    try:
                        repo.append(new_record)
                        display_success("Contact saved successfully!")
                        st.rerun()
                    except Exception as e:
                        display_error(str(e))

    st.subheader("Manage Contacts")
    if not df.is_empty():
        pd_df = df.to_pandas()
        edited_df = st.data_editor(
            pd_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "ID": None,
                "LinkedIn": st.column_config.LinkColumn("LinkedIn")
            },
            key="contact_editor"
        )
        
        if st.button("Save Changes to Contacts", type="primary"):
            try:
                updated_polars_df = pl.from_pandas(edited_df)
                updated_polars_df = updated_polars_df.cast(CONTACT_SCHEMA)
                repo.save(updated_polars_df)
                display_success("Contacts updated successfully!")
                st.rerun()
            except Exception as e:
                display_error(f"Failed to save changes: {str(e)}")
    else:
        st.info("Your contacts list is empty.")

if __name__ == "__main__":
    main()