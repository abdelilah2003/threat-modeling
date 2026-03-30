
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY rag /app/rag
COPY model /app/model
COPY ai_release.yaml /app/ai_release.yaml

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "/app", "--host", "0.0.0.0", "--port", "8000"]
