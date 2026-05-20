import os

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def _connection_config():
    try:
        mysql = st.secrets.get("mysql")
    except Exception:
        mysql = None

    if mysql:
        return {
            "host": mysql.get("host"),
            "port": mysql.get("port", 3306),
            "database": mysql["database"],
            "user": mysql["user"],
            "password": mysql["password"],
            "cloud_sql_connection_name": mysql.get("cloud_sql_connection_name"),
        }

    return {
        "host": os.environ.get("MYSQL_HOST"),
        "port": os.environ.get("MYSQL_PORT", "3306"),
        "database": os.environ["MYSQL_DATABASE"],
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "cloud_sql_connection_name": os.environ.get("CLOUD_SQL_CONNECTION_NAME"),
    }


def _bot_connection_config():
    base_config = _connection_config()

    try:
        ai_mysql = st.secrets.get("ai_mysql")
    except Exception:
        ai_mysql = None

    if ai_mysql:
        return {
            "host": ai_mysql.get("host", base_config["host"]),
            "port": ai_mysql.get("port", base_config["port"]),
            "database": ai_mysql.get("database", base_config["database"]),
            "user": ai_mysql.get("user", "BOT"),
            "password": ai_mysql["password"],
            "cloud_sql_connection_name": ai_mysql.get(
                "cloud_sql_connection_name",
                base_config["cloud_sql_connection_name"],
            ),
        }

    bot_password = os.environ.get("AI_MYSQL_PASSWORD")
    if not bot_password:
        raise RuntimeError("AI_MYSQL_PASSWORD is required for chatbot database access.")

    base_config["user"] = os.environ.get("AI_MYSQL_USER", "BOT")
    base_config["password"] = bot_password
    return base_config


def _create_mysql_engine(mysql):
    if mysql["cloud_sql_connection_name"]:
        return create_engine(
            URL.create(
                "mysql+pymysql",
                username=mysql["user"],
                password=mysql["password"],
                database=mysql["database"],
                query={
                    "unix_socket": f"/cloudsql/{mysql['cloud_sql_connection_name']}",
                },
            )
        )

    return create_engine(
        URL.create(
            "mysql+pymysql",
            username=mysql["user"],
            password=mysql["password"],
            host=mysql["host"],
            port=int(mysql["port"]),
            database=mysql["database"],
        )
    )


@st.cache_resource
def get_engine():
    return _create_mysql_engine(_connection_config())


@st.cache_resource
def get_bot_engine():
    return _create_mysql_engine(_bot_connection_config())
