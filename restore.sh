#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./restore.sh [backup_file]"
  exit 1
fi

# Check if file exists
if [ ! -f "$1" ]; then
  echo "Error: Backup file not found"
  exit 1
fi

# Restore from backup
cat "$1" | docker exec -i hospital-system_database_1 psql -U hospital_admin hospital_db

echo "Database restored from $1"
