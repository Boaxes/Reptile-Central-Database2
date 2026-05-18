import pytest

from backend.ai_chatbot import RateLimitExceeded, check_rate_limit, classify_question


def test_routes_customer_spend_question_to_sql():
    assert classify_question("What customer spent the most this year?") == "sql"


def test_routes_temperature_question_to_care():
    assert classify_question("What temperature should a ball python have?") == "care"


def test_rate_limit_blocks_eleventh_request():
    state = {}

    for idx in range(10):
        check_rate_limit(state, now=float(idx), limit=10, window_seconds=3600)

    with pytest.raises(RateLimitExceeded):
        check_rate_limit(state, now=11.0, limit=10, window_seconds=3600)


def test_rate_limit_expires_old_requests():
    state = {}

    for idx in range(10):
        check_rate_limit(state, now=float(idx), limit=10, window_seconds=3600)

    check_rate_limit(state, now=3601.0, limit=10, window_seconds=3600)
    assert state["ai_chat_request_timestamps"][-1] == 3601.0
