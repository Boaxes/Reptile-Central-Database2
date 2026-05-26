import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import MutableMapping

import streamlit as st


CARE_MANUALS_DIR = Path(__file__).resolve().parent / "care_sheets" / "manuals"
DEFAULT_AI_MODEL = "gpt-4o-mini"
DEFAULT_EMBED_MODEL = "text-embedding-3-small"
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60 * 60
RATE_LIMIT_SESSION_KEY = "ai_chat_request_timestamps"
SQL_TABLES = [
    "Customers",
    "Employees",
    "Orders",
    "ProductTypes",
    "Products",
    "Animals",
    "OrderDetails",
    "EmployeeAnimals",
]
SQL_KEYWORDS = {
    "animal",
    "animals",
    "available",
    "customer",
    "customers",
    "employee",
    "employees",
    "inventory",
    "order",
    "orders",
    "product",
    "products",
    "revenue",
    "sale",
    "sales",
    "sold",
    "spent",
    "stock",
    "total",
}
CARE_KEYWORDS = {
    "basking",
    "care",
    "diet",
    "enclosure",
    "feed",
    "feeding",
    "heat",
    "humidity",
    "lighting",
    "substrate",
    "supplement",
    "temp",
    "temperature",
    "uvb",
    "water",
}


@dataclass
class ChatbotAnswer:
    text: str
    mode: str
    sql: str | None = None


class RateLimitExceeded(Exception):
    """Raised when a Streamlit session has used its chatbot request quota."""


def check_rate_limit(
    state: MutableMapping,
    now: float | None = None,
    limit: int = RATE_LIMIT_REQUESTS,
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
) -> None:
    """Track chatbot requests in the current session before any LLM call is made."""
    now = now if now is not None else time.time()
    timestamps = [
        ts for ts in state.get(RATE_LIMIT_SESSION_KEY, []) if now - float(ts) < window_seconds
    ]

    if len(timestamps) >= limit:
        retry_after = int(window_seconds - (now - float(timestamps[0])))
        minutes = max(1, retry_after // 60)
        raise RateLimitExceeded(
            f"Chat limit reached. Please wait about {minutes} minute(s) before asking again."
        )

    timestamps.append(now)
    state[RATE_LIMIT_SESSION_KEY] = timestamps


def classify_question(question: str) -> str:
    lowered = question.lower()
    care_hits = sum(1 for keyword in CARE_KEYWORDS if keyword in lowered)
    sql_hits = sum(1 for keyword in SQL_KEYWORDS if keyword in lowered)
    return "sql" if sql_hits > care_hits else "care"


def _require_openai_key() -> None:
    if os.environ.get("OPENAI_API_KEY"):
        return

    try:
        openai_secrets = st.secrets.get("openai")
    except Exception:
        openai_secrets = None

    api_key = None
    if openai_secrets:
        api_key = openai_secrets.get("api_key")
    else:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            api_key = None

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        return

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for the AI Chatbot.")


def _configure_llama_index():
    _require_openai_key()

    try:
        from llama_index.core import Settings
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("LlamaIndex dependencies are not installed.") from exc

    llm = OpenAI(model=os.environ.get("AI_MODEL", DEFAULT_AI_MODEL), temperature=0.1)
    embed_model = OpenAIEmbedding(model=os.environ.get("AI_EMBED_MODEL", DEFAULT_EMBED_MODEL))
    Settings.llm = llm
    Settings.embed_model = embed_model
    return llm


@st.cache_resource
def get_care_query_engine():
    _configure_llama_index()

    try:
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    except ImportError as exc:
        raise RuntimeError("LlamaIndex dependencies are not installed.") from exc

    documents = SimpleDirectoryReader(
        input_dir=str(CARE_MANUALS_DIR),
        required_exts=[".md"],
        recursive=False,
    ).load_data()
    if not documents:
        raise RuntimeError(f"No care manuals found in {CARE_MANUALS_DIR}.")

    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine(similarity_top_k=4)


@st.cache_resource
def get_sql_query_engine(_engine):
    llm = _configure_llama_index()

    try:
        from llama_index.core import SQLDatabase
        from llama_index.core.query_engine import NLSQLTableQueryEngine
    except ImportError as exc:
        raise RuntimeError("LlamaIndex SQL dependencies are not installed.") from exc

    sql_database = SQLDatabase(_engine, include_tables=SQL_TABLES)
    return NLSQLTableQueryEngine(sql_database=sql_database, tables=SQL_TABLES, llm=llm)


def answer_care_question(question: str) -> ChatbotAnswer:
    query_engine = get_care_query_engine()
    response = query_engine.query(
        "Answer using only the internal reptile care manuals. "
        "If the manuals do not contain the answer, say so briefly.\n\n"
        f"Question: {question}"
    )
    return ChatbotAnswer(text=str(response), mode="Care Sheets")


def answer_sql_question(question: str, engine) -> ChatbotAnswer:
    query_engine = get_sql_query_engine(engine)
    response = query_engine.query(question)
    metadata = getattr(response, "metadata", {}) or {}
    sql = metadata.get("sql_query") or metadata.get("query_code")
    return ChatbotAnswer(text=str(response), mode="Database", sql=sql)


def answer_question(question: str, engine: object = None, mode: str = "Auto") -> ChatbotAnswer:
    selected_mode = mode.lower()
    route = classify_question(question) if selected_mode == "auto" else selected_mode

    if route in {"sql", "database"}:
        return answer_sql_question(question, engine)

    return answer_care_question(question)
