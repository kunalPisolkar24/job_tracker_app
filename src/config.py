import polars as pl

JOB_STATUSES =["Saved", "Applied", "Interviewing", "Offer", "Rejected", "No Response"]

JOB_SCHEMA = {
    "ID": pl.Utf8,
    "Company": pl.Utf8,
    "Title": pl.Utf8,
    "Location": pl.Utf8,
    "Status": pl.Utf8,
    "Date_Applied": pl.Utf8,
    "Salary": pl.Utf8,
    "Notes": pl.Utf8
}

CONTACT_SCHEMA = {
    "ID": pl.Utf8,
    "Name": pl.Utf8,
    "Company": pl.Utf8,
    "Email": pl.Utf8,
    "Phone": pl.Utf8,
    "LinkedIn": pl.Utf8,
    "Notes": pl.Utf8
}

DATA_DIR = "data"
JOBS_FILE = f"{DATA_DIR}/applications.csv"
CONTACTS_FILE = f"{DATA_DIR}/contacts.csv"