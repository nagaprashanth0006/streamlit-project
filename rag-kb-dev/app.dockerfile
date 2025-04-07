FROM python:3.11-slim
RUN useradd -ms /bin/bash appuser

WORKDIR /app
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

USER appuser
CMD ["python", "main.py"]
