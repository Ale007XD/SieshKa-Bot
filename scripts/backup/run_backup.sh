#!/bin/bash
# Backup script for PostgreSQL database

set -e

# Configuration from environment
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_COMPRESS_LEVEL="${BACKUP_COMPRESS_LEVEL:-6}"

# Database configuration
DB_NAME="${POSTGRES_DB:-food_delivery}"
DB_USER="${POSTGRES_USER:-food_delivery}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="backup_${DB_NAME}_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

echo "Starting backup at $(date)"
echo "Backup file: ${BACKUP_FILENAME}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Run pg_dump
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F c \
    -f "${BACKUP_PATH}.dump"

# Compress backup
echo "Compressing backup..."
gzip -${BACKUP_COMPRESS_LEVEL} "${BACKUP_PATH}.dump"
BACKUP_FILE="${BACKUP_PATH}.dump.gz"

# Get file size
FILE_SIZE_MB=$(du -m "${BACKUP_FILE}" | cut -f1)
echo "Backup size: ${FILE_SIZE_MB} MB"

# Verify backup integrity
echo "Verifying backup..."
if gzip -t "${BACKUP_FILE}"; then
    echo "Backup verification passed"
else
    echo "ERROR: Backup verification failed!"
    exit 1
fi

# Check pg_restore list
if pg_restore --list "${BACKUP_FILE}" > /dev/null 2>&1; then
    echo "pg_restore list check passed"
else
    echo "WARNING: pg_restore list check failed"
fi

# Rotate old backups
echo "Rotating old backups..."
find "${BACKUP_DIR}" -name "backup_*.dump.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete

echo "Backup completed successfully at $(date)"
echo "Backup file: ${BACKUP_FILE}"

# Send to Telegram if enabled
if [ "${BACKUP_ENABLED}" = "true" ] && [ -n "${BACKUP_TG_CHAT_ID}" ]; then
    python scripts/backup/send_to_telegram.py "${BACKUP_FILE}" "${FILE_SIZE_MB}"
fi
