import polars as pl
import streamlit as st

from src.config import CONTACTS_FILE, CONTACT_SCHEMA
from src.repository import CsvRepository
from src.ui_components import apply_custom_theme, display_error, display_success

st.set_page_config(page_title="Network Contacts", page_icon="🤝", layout="wide")
apply_custom_theme()


def build_contact_record(
    name: str,
    company: str,
    email: str,
    phone: str,
    linkedin: str,
    notes: str,
) -> dict[str, str]:
    return {
        "ID": "",
        "Name": name.strip(),
        "Company": company.strip(),
        "Email": email.strip(),
        "Phone": phone.strip(),
        "LinkedIn": linkedin.strip(),
        "Notes": notes.strip(),
    }


def normalize_contact_editor_frame(df) -> pl.DataFrame:
    normalized = df.reindex(columns=list(CONTACT_SCHEMA.keys()), fill_value="").copy()

    for column in normalized.columns:
        normalized[column] = normalized[column].fillna("").astype(str).str.strip()

    return pl.from_pandas(normalized).cast(CONTACT_SCHEMA)


def render_add_contact_form(repo: CsvRepository) -> None:
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

            if not submitted:
                return

            if not name.strip() or not company.strip():
                display_error("Name and Company are required.")
                return

            try:
                record = build_contact_record(
                    name=name,
                    company=company,
                    email=email,
                    phone=phone,
                    linkedin=linkedin,
                    notes=notes,
                )
                repo.append(record)
                display_success("Contact saved successfully!")
                st.rerun()
            except Exception as exc:
                display_error(str(exc))


def render_contact_editor(repo: CsvRepository, df: pl.DataFrame) -> None:
    st.subheader("Manage Contacts")

    if df.is_empty():
        st.info("Your contacts list is empty.")
        return

    edited_df = st.data_editor(
        df.to_pandas(),
        width="stretch",
        num_rows="dynamic",
        column_config={
            "ID": None,
            "LinkedIn": st.column_config.LinkColumn("LinkedIn"),
        },
        key="contact_editor",
    )

    if not st.button("Save Changes to Contacts", type="primary"):
        return

    try:
        updated_df = normalize_contact_editor_frame(edited_df)
        repo.save(updated_df)
        display_success("Contacts updated successfully!")
        st.rerun()
    except Exception as exc:
        display_error(f"Failed to save changes: {exc}")


def main() -> None:
    st.title("Network & Referrals")

    try:
        repo = CsvRepository(CONTACTS_FILE, CONTACT_SCHEMA)
        df = repo.get_all()
    except Exception as exc:
        display_error(str(exc))
        return

    render_add_contact_form(repo)
    render_contact_editor(repo, df)


if __name__ == "__main__":
    main()
