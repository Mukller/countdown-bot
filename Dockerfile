FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser 2>/dev/null || true
RUN chown -R appuser:appuser /app 2>/dev/null || true
USER appuser
CMD ["python", "-u", "-m", "app.main"]

# Author: Anton Petnitsky
# GitHub: https://github.com/Mukller/countdown-bot
# Last modified: 2026-05-16 01:38:14 +0300
