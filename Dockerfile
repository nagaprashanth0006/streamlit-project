# #FROM python:3.11 as base
# FROM python:3.11-slim as base
# WORKDIR /app
# COPY requirements.txt .
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     gcc \
#     libffi-dev \
#     && rm -rf /var/lib/apt/lists/*

# RUN pip install -r requirements.txt --no-cache-dir && rm -rf /root/.cache

# FROM python:3.11-slim as main
# WORKDIR /app
# COPY --from=base /app /app
# COPY app.py /app/app.py
# #RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# #USER appuser
# EXPOSE 8501
# ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]





FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]