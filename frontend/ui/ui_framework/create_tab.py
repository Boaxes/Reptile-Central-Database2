#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file renders reusable create tabs backed by the generic create stored procedure.

import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from backend.db import get_engine
from frontend.ui.ui_framework.common import (
    SUCCESS_MESSAGE_DURATION_SECONDS,
    queue_success_message,
    render_success_message,
)
from frontend.ui.ui_framework.data_access import sql_error_message
from frontend.ui.ui_framework.forms import (
    collect_invalid_pattern_fields,
    collect_missing_required_fields,
    form_field_key,
    format_select_option,
    normalize_text,
    render_missing_select_options,
    resolve_select_value,
    select_default_index,
)


def render_create_tab(
    tab,
    name: str,
    create_id: str,
    specs: list[dict],
    form_key: str,
    submit_label: str,
    success_duration_seconds: int = SUCCESS_MESSAGE_DURATION_SECONDS,
) -> None:
    """Render a generic create tab powered by sp_generic_create with up to four inputs."""
    if len(specs) > 4:
        raise ValueError("render_create_tab supports at most 4 fields (p1..p4).")
    success_key = f"create_success_{create_id}_{form_key}"

    with tab:
        st.subheader(name)
        engine = get_engine()
        form_version_key = f"{form_key}_version"
        form_version = int(st.session_state.get(form_version_key, 0))

        with st.form(form_key):
            p = {"p1": None, "p2": None, "p3": None, "p4": None}

            for idx, s in enumerate(specs):
                param = f"p{idx + 1}"
                label = s["label"]
                ftype = s["type"]

                if ftype == "text":
                    raw = st.text_input(
                        label,
                        placeholder=s.get("placeholder"),
                        help=s.get("help"),
                        key=form_field_key(form_key, param, form_version),
                    )
                    p[param] = normalize_text(raw)

                elif ftype == "int":
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=s.get("default", 0),
                        step=s.get("step", 1),
                        help=s.get("help"),
                        key=form_field_key(form_key, param, form_version),
                    )
                    p[param] = int(num)

                elif ftype == "decimal":
                    num = st.number_input(
                        label,
                        min_value=s.get("min", None),
                        max_value=s.get("max", None),
                        value=s.get("default", 0.0),
                        step=s.get("step", 0.01),
                        help=s.get("help"),
                        key=form_field_key(form_key, param, form_version),
                    )
                    p[param] = float(num)

                elif ftype == "select":
                    option_list = s.get("options", [])
                    if not option_list:
                        render_missing_select_options(label, s)
                        return

                    default_index = select_default_index(option_list, s.get("default"))
                    selected_option = st.selectbox(
                        label,
                        option_list,
                        index=default_index,
                        format_func=format_select_option(s),
                        help=s.get("help"),
                        key=form_field_key(form_key, param, form_version),
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
                        text("CALL sp_generic_create(:create_id, :p1, :p2, :p3, :p4);"),
                        {"create_id": create_id, **p},
                    )
            except DBAPIError as exc:
                st.error(sql_error_message(exc))
                return
            st.session_state[form_version_key] = form_version + 1
            queue_success_message(success_key, "Record created successfully.")
            st.cache_data.clear()
            st.rerun()

        render_success_message(success_key, success_duration_seconds)
