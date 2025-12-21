FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8501/healthz')"

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]