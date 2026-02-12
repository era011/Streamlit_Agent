FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
EXPOSE 8501
CMD ["sh", "-c", "streamlit run frontend/ui.py --server.port=${PORT} --server.address=0.0.0.0"]

