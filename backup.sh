#!/bin/bash

# Set date format for backup filename
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backups directory if it doesn't exist
mkdir -p backups

# Backup the database
docker exec hospital-system_database_1 pg_dump -U hospital_admin hospital_db > backups/hospital_backup_$DATE.sql

echo "Backup created: backups/hospital_backup_$DATE.sql"
