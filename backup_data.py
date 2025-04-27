#!/usr/bin/env python
"""
Database backup utility for the Energy Anomaly Detection System

This script creates a backup of the SQLite database to ensure data persistence
even when working offline.
"""
import os
import sys
import shutil
import datetime
import sqlite3
from pathlib import Path

DB_FILE = "energy_anomaly_detection.db"
BACKUP_DIR = "data_backups"

def main():
    """Execute the database backup"""
    # Check if database exists
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found. No backup created.")
        return
    
    # Create backup directory if it doesn't exist
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}_{DB_FILE}")
    
    # Create backup
    try:
        # Make sure the database is not locked
        source_conn = sqlite3.connect(DB_FILE)
        source_conn.close()
        
        # Copy the database file
        shutil.copy2(DB_FILE, backup_file)
        print(f"Backup created successfully: {backup_file}")
        
        # Clean up old backups (keep last 5)
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
                print(f"Removed old backup: {old_backup}")
    
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

if __name__ == "__main__":
    main()