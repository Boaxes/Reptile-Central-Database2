#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file renders reusable update tabs backed by the generic update stored procedure.

import pandas as pd
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
from frontend.ui.ui_framework.forms import (
    build_display_labels,
    collect_invalid_pattern_fields,
    collect_missing_required_fields,
    format_select_option,
    normalize_text,
    render_missing_select_options,
    resolve_select_value,
    select_default_index,
)


def render_update_tab(
    tab,
    name: str,
    view: str,
    update_id: str,
    target_id: str,
    label_field_1: str,
    label_field_2: str = None,
    label_field_3: str = None,
    label_formatter=None,
    specs: list[dict] | None = None,
    form_key: str = "update_form",
    submit_label: str = "Update",
    success_duration_seconds: int = SUCCESS_MESSAGE_DURATION_SECONDS,
) -> None:
    """Render a generic update tab powered by sp_generic_update with up to four inputs."""
    specs = specs or []
    if len(specs) > 4:
        raise ValueError("render_update_tab supports at most 4 fields (p1..p4).")
    success_key = f"update_success_{view}_{target_id}_{form_key}"

    with tab:
        st.subheader(name)
        engine = get_engine()
        df = fetch_view(view)

        if df.empty:
            st.write("No records to update.")
            return

        if target_id not in df.columns:
            raise ValueError(f"Target id column '{target_id}' not found in view '{view}'.")

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
            key=f"{form_key}_record_selector",
        )
        row = df.loc[selected_idx]
        selected_target_id = row[target_id]

        with st.form(form_key, clear_on_submit=True):
            p = {"p1": None, "p2": None, "p3": None, "p4": None}

            for idx, s in enumerate(specs):
                param = f"p{idx + 1}"
                label = s["label"]
                ftype = s["type"]
                source_col = s.get("source")

                if source_col and source_col not in df.columns:
                    raise ValueError(f"Source column '{source_col}' not found in view '{view}'.")

                source_val = row[source_col] if source_col else None

                if ftype == "text":
                    raw = st.text_input(
                        label,
                        value="" if pd.isna(source_val) else str(source_val),
                        placeholder=s.get("placeholder"),
                        help=s.get("help"),
                    )
                    p[param] = normalize_text(raw)

                elif ftype == "int":
                    default_val = int(source_val)
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=default_val,
                        step=s.get("step", 1),
                        help=s.get("help"),
                    )
                    p[param] = int(num)

                elif ftype == "decimal":
                    default_val = float(source_val)
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=default_val,
                        step=s.get("step", 0.01),
                        help=s.get("help"),
                    )
                    p[param] = float(num)

                elif ftype == "select":
                    option_list = s.get("options", [])
                    if not option_list:
                        render_missing_select_options(label, s)
                        return

                    default_index = select_default_index(option_list, source_val)
                    selected_option = st.selectbox(
                        label,
                        option_list,
                        index=default_index,
                        format_func=format_select_option(s),
                        help=s.get("help"),
                    )
                    p[param] = resolve_select_value(selected_option, s.get("value_map"))

                else:
                    raise ValueError(f"Unsupported type '{ftype}' for '{label}'")

            submitted = st.form_submit_button(submit_label)

        if submitted:
            missing_fields = collect_missing_required_fields(specs, p)
            if missing_fields:
                st.error(f"Please fill out: {', '.join(missing_fields)}.")
                return
            pattern_errors = collect_invalid_pattern_fields(specs, p)
            if pattern_errors:
                st.error(pattern_errors[0])
                return

            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("CALL sp_generic_update(:update_id, :target_id, :p1, :p2, :p3, :p4);"),
                        {"update_id": update_id, "target_id": str(selected_target_id), **p},
                    )
            except DBAPIError as exc:
                st.error(sql_error_message(exc))
                return
            queue_success_message(success_key, "Record updated successfully.")
            st.cache_data.clear()
            st.rerun()

        render_success_message(success_key, success_duration_seconds)
