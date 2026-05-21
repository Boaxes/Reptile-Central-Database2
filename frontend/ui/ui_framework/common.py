#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file contains shared page setup and success message helpers used across Streamlit pages.

import streamlit as st

from frontend.ui.reset_button import render_reset_button


SUCCESS_MESSAGE_DURATION_SECONDS = 3


def page_setup(title: str, icon: str, page_heading: str = None) -> None:
    """Configure a Streamlit page and render the reset database button."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    st.sidebar.markdown(
        """
<style>
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[href$="/Reptibot"] {
    display: none;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[href$="/Care_Sheets"] {
    display: none;
}
section[data-testid="stSidebar"] hr {
    display: none;
}
section[data-testid="stSidebar"] a[href$="/Care_Sheets"] {
    background: #2e7d32;
    border-radius: 6px;
    padding: 6px 10px;
}
section[data-testid="stSidebar"] a[href$="/Care_Sheets"] span {
    color: white !important;
    font-weight: 600;
}
</style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.page_link("pages/00_Reptibot.py", label="🐍 Reptibot")
    st.sidebar.page_link("pages/09_Care_Sheets.py", label="📋 Care Sheets")
    render_reset_button(key="reset_db_button")

    if page_heading:
        st.title(page_heading)


def queue_success_message(key: str, message: str) -> None:
    """Store a success message so it can be shown after st.rerun()."""
    st.session_state[key] = message


def render_success_message(key: str, duration_seconds: int = SUCCESS_MESSAGE_DURATION_SECONDS) -> None:
    """Render and clear a queued success message without blocking reruns."""
    message = st.session_state.pop(key, None)
    if message:
        st.success(message)
