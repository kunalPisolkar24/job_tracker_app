import streamlit as st


class ThemeManager:
    @staticmethod
    def apply_custom_theme() -> None:
        st.markdown(
            """
            <style>
            html, body, [class*="css"] {
                font-family: "Segoe UI", "Noto Sans", "Helvetica Neue", Arial, sans-serif;
            }

            div[data-testid="metric-container"] {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                padding: 5% 5% 5% 10%;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }

            .stButton > button {
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s ease;
                width: 100%;
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def apply_custom_theme() -> None:
    ThemeManager.apply_custom_theme()


def display_error(msg: str) -> None:
    st.error(msg, icon="🚨")


def display_success(msg: str) -> None:
    st.success(msg, icon="✅")
