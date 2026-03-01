# Job Tracker App

A Streamlit-based job search tracker with web and desktop modes.

## Features
- Track job applications with status, dates, salary, and notes
- Manage network/referral contacts
- View dashboard metrics and charts for application progress
- Run as a browser app or desktop window

## Tech Stack
- Python
- Streamlit
- Polars
- Plotly
- PyWebView

## Quick Start
```bash
make setup
```

Run in browser:
```bash
make run-web
```

Run as desktop app:
```bash
make run-desktop
```

Build desktop executable:
```bash
make build-desktop
```

## Data Storage
- `data/applications.csv`
- `data/contacts.csv`