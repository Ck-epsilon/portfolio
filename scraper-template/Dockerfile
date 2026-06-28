# Author: Ck.epsilon
# Multi-Site Web Scraper — Docker image for Premium tier
#
# Build:  docker build -t scraper .
# Run:    docker run --rm scraper --config sites/example.yaml
# Cron:   docker run --rm scraper scheduler --config sites/example.yaml --every 1h

FROM python:3.12-slim

WORKDIR /app

# Install system deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps chromium

COPY . .

ENTRYPOINT ["python"]
CMD ["run.py", "--help"]
