# Using official python 3.11 slim image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

COPY . .

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir . && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["sentinel", "-c", "targets.yaml"]
