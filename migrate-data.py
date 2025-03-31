#!/usr/bin/env python3
"""
Caldera Data Migration Script

This script migrates data from the old pickle format to the new JSON format.
It creates a backup of the original data before migration.
"""

import os
import sys
import pickle
import json
import shutil
import datetime
import argparse
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.getcwd())

# Import Caldera JSON serializer
try:
    from app.utility.json_serializer import CalderaJSONEncoder
except ImportError:
    print("Error: Could not import Caldera JSON serializer. Make sure you're running this script from the Caldera root directory.")
    sys.exit(1)

def backup_data_directory(backup_dir=None):
    """
    Create a backup of the data directory.
    
    Args:
        backup_dir: Optional directory to store the backup
        
    Returns:
        Path to the backup directory
    """
    if not backup_dir:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = f"data/backup/migrate-{timestamp}"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy data files
    if os.path.exists("data/object_store"):
        shutil.copy2("data/object_store", os.path.join(backup_dir, "object_store"))
        print(f"Backed up data/object_store to {backup_dir}/object_store")
    
    return backup_dir

def migrate_pickle_to_json(backup_first=True, backup_dir=None):
    """
    Migrate data from pickle to JSON format.
    
    Args:
        backup_first: Whether to create a backup before migration
        backup_dir: Optional directory to store the backup
        
    Returns:
        True if migration was successful, False otherwise
    """
    # Check if pickle data exists
    if not os.path.exists("data/object_store"):
        print("No pickle data found at data/object_store. Nothing to migrate.")
        return False
    
    # Create backup if requested
    if backup_first:
        backup_dir = backup_data_directory(backup_dir)
        print(f"Created backup in {backup_dir}")
    
    try:
        # Load pickle data
        print("Loading pickle data...")
        with open("data/object_store", "rb") as f:
            data = pickle.load(f)
        
        # Convert to JSON
        print("Converting to JSON format...")
        json_data = json.dumps(data, cls=CalderaJSONEncoder, indent=2)
        
        # Save JSON data
        print("Saving JSON data...")
        with open("data/object_store.json", "w") as f:
            f.write(json_data)
        
        print("Migration completed successfully!")
        print("JSON data saved to data/object_store.json")
        
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Migrate Caldera data from pickle to JSON format")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup before migration")
    parser.add_argument("--backup-dir", help="Directory to store the backup")
    args = parser.parse_args()
    
    print("Caldera Data Migration Tool")
    print("==========================")
    
    # Check if running from Caldera root directory
    if not os.path.exists("server.py") or not os.path.exists("data"):
        print("Error: This script must be run from the Caldera root directory.")
        sys.exit(1)
    
    # Migrate data
    success = migrate_pickle_to_json(
        backup_first=not args.no_backup,
        backup_dir=args.backup_dir
    )
    
    if success:
        print("\nMigration completed successfully!")
        print("You can now start Caldera with the new JSON data format.")
    else:
        print("\nMigration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
