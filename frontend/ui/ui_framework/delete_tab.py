#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file renders reusable delete tabs backed by the generic delete stored procedure.

import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from backend.db import get_engine
from frontend.ui.ui_framework.common import (
    SUCCESS_MESSAGE_DURATION_SECONDS,
    queue_success_message,
    render_success_message,
)
from frontend.ui.ui_framework.data_access import fetch_view, sql_error_message
from frontend.ui.ui_framework.forms import build_display_labels


def render_delete_tab(
    tab,
    name: str,
    view: str,
    delete_id: str,
    label_field_1: str,
    label_field_2: str = None,
    label_field_3: str = None,
    label_formatter=None,
    success_duration_seconds: int = SUCCESS_MESSAGE_DURATION_SECONDS,
) -> None:
    """Render a generic delete tab powered by sp_generic_delete."""
    success_key = f"delete_success_{view}_{delete_id}"

    with tab:
        st.subheader(name)
        engine = get_engine()
        df = fetch_view(view)
        key_suffix = f"{view}_{delete_id}".replace(" ", "_").replace("`", "").replace(".", "_")

        if df.empty:
            st.write("No records to delete.")
            render_success_message(success_key, success_duration_seconds)
            return

        if delete_id not in df.columns:
            raise ValueError(f"Delete id column '{delete_id}' not found in view '{view}'.")

        label_fields = [field for field in [label_field_1, label_field_2, label_field_3] if field]
        df = df.copy()
        if label_formatter:
            df["_display_label"] = df.apply(label_formatter, axis=1)
        else:
            df["_display_label"] = build_display_labels(df, label_fields)
        options = df.index.tolist()

        selected_idx = st.selectbox(
            "Select Record",
            options,
            format_func=lambda i: df.loc[i, "_display_label"],
            key=f"delete_select_{key_suffix}",
        )
        selected_id = df.loc[selected_idx, delete_id]

        if st.button("Delete", key=f"delete_button_{key_suffix}"):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            CALL sp_generic_delete(
                                :delete_id,
                                :target_id
                            );
                            """
                        ),
                        {
                            "delete_id": delete_id,
                            "target_id": str(selected_id),
                        },
                    )
            except DBAPIError as exc:
                st.error(sql_error_message(exc))
                return
            queue_success_message(success_key, "Record deleted successfully.")
            st.cache_data.clear()
            st.rerun()

        render_success_message(success_key, success_duration_seconds)
