# Author: Ck.epsilon & Chaos (AI Programming Assistant)
# AI Agent Workbench — Docker image (Premium tier)
#
# Build:  docker build -t ai-workbench .
# Run:    docker run -p 8000:8000 ai-workbench

FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
