#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file renders paginated browse tabs backed by database views.

import streamlit as st

from frontend.ui.ui_framework.data_access import fetch_view


PAGE_SIZE_OPTIONS: list[int | str] = [10, 25, 50, 100, "All"]
DEFAULT_PAGE_SIZE = 10
DATAFRAME_ROW_HEIGHT_PX = 35
DATAFRAME_HEADER_HEIGHT_PX = 38


def _dataframe_height(num_rows: int) -> int:
    return DATAFRAME_HEADER_HEIGHT_PX + max(1, num_rows) * DATAFRAME_ROW_HEIGHT_PX + 2


@st.fragment
def _render_paginated_browse(view: str) -> None:
    df = fetch_view(view)
    total = len(df)
    size_key = f"page_size_{view}"
    idx_key = f"page_idx_{view}"

    current_size = st.session_state.get(size_key, DEFAULT_PAGE_SIZE)
    if current_size not in PAGE_SIZE_OPTIONS:
        current_size = DEFAULT_PAGE_SIZE

    if current_size == "All" or total == 0:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            height=_dataframe_height(total),
        )
        _, cap_col, _, _, size_col = st.columns([1, 4, 1, 2, 2])
        size_col.selectbox(
            "Rows per page",
            PAGE_SIZE_OPTIONS,
            index=PAGE_SIZE_OPTIONS.index(current_size),
            key=size_key,
            label_visibility="collapsed",
        )
        cap_col.markdown(
            f"<div style='text-align:center; padding-top:0.4rem;'>"
            f"Showing {total} of {total} rows</div>",
            unsafe_allow_html=True,
        )
        return

    page_size = int(current_size)
    max_page = max(0, (total - 1) // page_size)
    page = max(0, min(int(st.session_state.get(idx_key, 0)), max_page))
    st.session_state[idx_key] = page

    start = page * page_size
    end = start + page_size
    visible = df.iloc[start:end]
    # Stable height for partial last pages so Prev/Next does not jump the layout.
    st.dataframe(
        visible,
        width="stretch",
        hide_index=True,
        height=_dataframe_height(page_size),
    )

    def _go_prev() -> None:
        cur = int(st.session_state.get(idx_key, 0))
        st.session_state[idx_key] = max(0, cur - 1)

    def _go_next() -> None:
        cur = int(st.session_state.get(idx_key, 0))
        st.session_state[idx_key] = min(max_page, cur + 1)

    prev_col, cap_col, next_col, _, size_col = st.columns([1, 4, 1, 2, 2])
    prev_col.button(
        "\u2039 Prev",
        key=f"prev_{view}",
        on_click=_go_prev,
        disabled=(page <= 0),
        width="stretch",
    )
    next_col.button(
        "Next \u203a",
        key=f"next_{view}",
        on_click=_go_next,
        disabled=(page >= max_page),
        width="stretch",
    )
    size_col.selectbox(
        "Rows per page",
        PAGE_SIZE_OPTIONS,
        index=PAGE_SIZE_OPTIONS.index(current_size),
        key=size_key,
        label_visibility="collapsed",
    )
    cap_col.markdown(
        f"<div style='text-align:center; padding-top:0.4rem;'>"
        f"Page {page + 1} of {max_page + 1} "
        f"&nbsp;&middot;&nbsp; rows {start + 1}&ndash;{min(end, total)} of {total}</div>",
        unsafe_allow_html=True,
    )


def render_browse_tab(tab, name: str, view: str) -> None:
    """Render a browse tab from a database view with pagination controls below."""
    with tab:
        st.subheader(name)
        _render_paginated_browse(view)
