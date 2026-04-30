# Using official python 3.11 slim image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Copy the code base
COPY . .

# Navigate to the respective directory for execution
WORKDIR /app/monitor

CMD ["python", "checker.py"]
