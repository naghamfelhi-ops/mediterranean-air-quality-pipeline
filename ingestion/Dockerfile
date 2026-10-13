FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY aq_ingest ./aq_ingest
COPY config ./config
ENV PYTHONPATH=/app
ENV LAKE_ROOT=/lake
