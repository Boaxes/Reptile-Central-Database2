FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY .streamlit ./.streamlit
COPY backend ./backend
COPY frontend ./frontend

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8080

CMD streamlit run frontend/Home.py --server.address=0.0.0.0 --server.port=${PORT:-8080} --server.headless=true
