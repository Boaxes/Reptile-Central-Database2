#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file contains shared form validation, formatting, and selectbox helper functions.

import re

import pandas as pd
import streamlit as st


def normalize_text(val: str) -> str | None:
    """Return None for blank strings so forms can submit SQL NULL values."""
    val = val.strip()
    return val or None


def collect_missing_required_fields(specs: list[dict], values: dict[str, object]) -> list[str]:
    """Return field labels that are required but missing."""
    missing: list[str] = []
    for idx, spec in enumerate(specs):
        # Keep this simple: text fields are required by default, others are opt-in.
        required = spec.get("required", spec.get("type") == "text")
        if not required:
            continue

        value = values.get(f"p{idx + 1}")
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(spec["label"])
    return missing


def collect_invalid_pattern_fields(specs: list[dict], values: dict[str, object]) -> list[str]:
    """Return validation error messages for pattern-constrained text fields."""
    errors: list[str] = []
    for idx, spec in enumerate(specs):
        pattern = spec.get("pattern")
        if not pattern:
            continue

        value = values.get(f"p{idx + 1}")
        if value is None:
            continue

        text_value = str(value).strip()
        if not text_value:
            continue

        if re.fullmatch(pattern, text_value) is None:
            errors.append(spec.get("pattern_message", f"Invalid value for {spec['label']}."))
    return errors


def form_field_key(form_key: str, param: str, version: int) -> str:
    """Build a stable, versioned widget key for form fields."""
    return f"{form_key}_{param}_{version}"


def build_display_labels(df: pd.DataFrame, label_fields: list[str]) -> pd.Series:
    """Build dropdown labels for selectbox submissions."""
    if not label_fields:
        raise ValueError("At least one label field is required.")

    missing = [field for field in label_fields if field not in df.columns]
    if missing:
        raise ValueError(f"Missing label fields in view data: {missing}")

    label_parts = [df[field].fillna("").astype(str).str.strip() for field in label_fields]
    display = label_parts[0]
    for part in label_parts[1:]:
        display = (display + " " + part).str.strip()

    return display.str.replace(r"\s+", " ", regex=True).str.strip()


def select_default_index(options: list, source_val: object, fallback: int = 0) -> int:
    """Find the best default option index by exact match."""
    if source_val in options:
        return options.index(source_val)
    return fallback


def resolve_select_value(selected_option: object, value_map: object) -> object:
    """Map a selected option to a stored value when value_map is provided."""
    return selected_option


def format_select_option(spec: dict):
    """Return a safe format function for select widgets."""
    return spec.get("format_func") or (lambda option: option)


def render_missing_select_options(label: str, spec: dict) -> None:
    """Render a user-facing message when a select field has no options."""
    st.write(spec.get("empty_options_message", f"No options available for {label}."))
