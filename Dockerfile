FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UZAA_DATABASE_PATH=/data/uzaapp.sqlite3 \
    UZAA_BACKUP_DIR=/backups

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 uzaapp \
    && useradd --create-home --uid 10001 --gid uzaapp uzaapp \
    && mkdir -p /data /backups \
    && chown -R uzaapp:uzaapp /app /data /backups

COPY --chown=uzaapp:uzaapp . .
USER uzaapp
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]