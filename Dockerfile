FROM python:3.10-slim

# Recreate minimal HTTPS-only apt sources and install system deps
RUN printf 'deb https://deb.debian.org/debian bookworm main\n\
deb https://deb.debian.org/debian bookworm-updates main\n\
deb https://security.debian.org/debian-security bookworm-security main\n' \
  > /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      poppler-utils \
      tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m spacy download en_core_web_sm

# Copy rest of the code
COPY . .

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
