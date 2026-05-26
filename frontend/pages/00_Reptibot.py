from pathlib import Path

import streamlit as st

from backend.ai_chatbot import answer_question, classify_question
from backend.db import get_bot_engine
from frontend.ui.ui_framework.common import page_setup


GECKO_AVATAR = str(
    Path(__file__).resolve().parents[1] / "assets" / "leopard_gecko.jpg"
)
INITIAL_MESSAGE = (
    "Hi! I'm Reptibot. Ask me about reptile care like feeding, temperatures, "
    "enclosures, or lighting, and I'll pull from our care sheet library. "
    "You can also ask business questions about customers, orders, animals, "
    "products, employees, or inventory and I'll query the database for you."
)
MESSAGE_LIMIT = 5
LIMIT_MESSAGE = (
    "You've reached the message limit for this session. "
    "Please refresh the page to start a new conversation."
)


page_setup(title="Reptibot", icon="🤖", page_heading="Reptibot")

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
debug_mode = st.session_state.debug_mode

if "ai_chat_messages" not in st.session_state:
    st.session_state.ai_chat_messages = [
        {"role": "assistant", "content": INITIAL_MESSAGE, "mode": None}
    ]

for message in st.session_state.ai_chat_messages:
    avatar = GECKO_AVATAR if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if debug_mode and message.get("sql"):
            st.code(message["sql"], language="sql")
        if message.get("mode"):
            st.caption(f"Mode: {message['mode']}")

user_message_count = sum(1 for m in st.session_state.ai_chat_messages if m["role"] == "user")
limit_reached = user_message_count >= MESSAGE_LIMIT

prompt = st.chat_input(
    "Ask about reptile care, sales, customers, orders, or inventory...",
    disabled=limit_reached,
)

if limit_reached and not any(m["content"] == LIMIT_MESSAGE for m in st.session_state.ai_chat_messages):
    st.session_state.ai_chat_messages.append({"role": "assistant", "content": LIMIT_MESSAGE, "mode": None})
    with st.chat_message("assistant", avatar=GECKO_AVATAR):
        st.markdown(LIMIT_MESSAGE)

if prompt and not limit_reached:
    if prompt.strip().upper() == "MOREINFO ON":
        st.session_state.debug_mode = True
        st.rerun()
    elif prompt.strip().upper() == "MOREINFO OFF":
        st.session_state.debug_mode = False
        st.rerun()

    st.session_state.ai_chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in st.session_state.ai_chat_messages[-6:]
        if m["role"] in ("user", "assistant") and m["content"] != INITIAL_MESSAGE
    )
    full_prompt = f"Conversation so far:\n{history}\n\nNew question: {prompt}" if history else prompt

    with st.chat_message("assistant", avatar=GECKO_AVATAR):
        try:
            with st.spinner("Thinking..."):
                engine = get_bot_engine() if classify_question(prompt) == "sql" else None
                response = answer_question(full_prompt, engine, "Auto")
        except Exception as exc:
            answer_text = f"Something went wrong: {exc}"
            st.error(answer_text)
            st.session_state.ai_chat_messages.append(
                {"role": "assistant", "content": answer_text, "mode": "Error"}
            )
        else:
            st.markdown(response.text)
            assistant_message = {
                "role": "assistant",
                "content": response.text,
                "mode": response.mode,
            }
            if response.sql:
                assistant_message["sql"] = response.sql
                if debug_mode:
                    st.code(response.sql, language="sql")
            st.caption(f"Mode: {response.mode}")
            st.session_state.ai_chat_messages.append(assistant_message)
