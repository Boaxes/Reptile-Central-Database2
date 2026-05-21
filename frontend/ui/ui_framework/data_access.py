#
# Citation for use of AI Tools:
# Date: 02/23/2026
# Prompts used to generate Python/Streamlit code
# We originally wrote each page by hand with repeated boilerplate for browse/create/update/delete tabs.
# With many iterative prompts, AI helped us design reusable shared UI framework files to unify common page logic.
# AI Source URL: https://chat.openai.com/
#
# This file provides cached database read helpers and SQL error handling for the UI.

import pandas as pd
import streamlit as st
from sqlalchemy.exc import PendingRollbackError

from backend.db import get_engine


UNKNOWN_SQL_ERROR_MESSAGE = "SQL ERROR: Unknown SQL Error. Please refresh the page and try again."


def is_pending_rollback_error(exc: Exception) -> bool:
    """Return True when pandas wraps SQLAlchemy's invalid transaction state."""
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, PendingRollbackError):
            return True

        message = str(current)
        if (
            "Can't reconnect until invalid transaction is rolled back" in message
            or "Please rollback() fully before proceeding" in message
        ):
            return True

        current = current.__cause__ or current.__context__

    return False


def read_sql_with_recovery(engine, query: str, params: dict | None = None) -> pd.DataFrame:
    """Run a read query and recover once from stale pooled transaction state."""
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params=params)
    except Exception as exc:
        if not is_pending_rollback_error(exc):
            raise
        engine.dispose()
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=300)
def fetch_view(view: str) -> pd.DataFrame:
    """Fetch all rows from a view, cached for 5 minutes."""
    return read_sql_with_recovery(get_engine(), f"SELECT * FROM {view};")


def sql_error_message(exc: Exception) -> str:
    """Extract the clean SQL message returned by stored procedures."""
    orig = getattr(exc, "orig", None)
    if orig is not None:
        args = getattr(orig, "args", None)
        if args and len(args) > 1 and args[1]:
            return str(args[1])
        text_value = str(orig).strip()
        if text_value:
            return text_value
        return UNKNOWN_SQL_ERROR_MESSAGE

    text_value = str(exc).strip()
    if text_value:
        return text_value
    return UNKNOWN_SQL_ERROR_MESSAGE
