FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8501
CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
