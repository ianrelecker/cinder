#!/usr/bin/env python3
"""
Migrate Caldera data to database.

This script migrates data from the current JSON/pickle storage to the new database system.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.getcwd())

# Import Caldera modules
try:
    from app.database.migration import migrate_all_data
    from app.database.service import DatabaseService
except ImportError:
    print("Error: Could not import Caldera modules. Make sure you're running this script from the Caldera root directory.")
    sys.exit(1)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Migrate Caldera data to database')
    parser.add_argument('--connection-string', help='Database connection string (SQLAlchemy format)')
    parser.add_argument('--db-type', choices=['sqlite', 'postgresql'], default='sqlite',
                        help='Database type (default: sqlite)')
    parser.add_argument('--db-path', default='data/caldera.db',
                        help='Path to SQLite database file (default: data/caldera.db)')
    parser.add_argument('--db-host', default='localhost',
                        help='PostgreSQL host (default: localhost)')
    parser.add_argument('--db-port', default='5432',
                        help='PostgreSQL port (default: 5432)')
    parser.add_argument('--db-name', default='caldera',
                        help='PostgreSQL database name (default: caldera)')
    parser.add_argument('--db-user', default='caldera',
                        help='PostgreSQL username (default: caldera)')
    parser.add_argument('--db-password', default='caldera',
                        help='PostgreSQL password (default: caldera)')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--backup', action='store_true',
                        help='Create a backup of the database before migration')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('migrate-to-db')
    
    # Check if running from Caldera root directory
    if not os.path.exists('server.py'):
        logger.error("This script must be run from the Caldera root directory")
        return 1
    
    # Determine connection string
    connection_string = args.connection_string
    if not connection_string:
        if args.db_type == 'sqlite':
            # Ensure data directory exists
            os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
            connection_string = f'sqlite:///{args.db_path}'
        else:
            connection_string = f'postgresql://{args.db_user}:{args.db_password}@{args.db_host}:{args.db_port}/{args.db_name}'
    
    # Set environment variables for database connection
    os.environ['CALDERA_DB_TYPE'] = args.db_type
    if args.db_type == 'sqlite':
        os.environ['CALDERA_DB_PATH'] = args.db_path
    else:
        os.environ['CALDERA_DB_HOST'] = args.db_host
        os.environ['CALDERA_DB_PORT'] = args.db_port
        os.environ['CALDERA_DB_NAME'] = args.db_name
        os.environ['CALDERA_DB_USER'] = args.db_user
        os.environ['CALDERA_DB_PASSWORD'] = args.db_password
    
    # Create database service
    logger.info(f"Connecting to database: {connection_string}")
    db_service = DatabaseService(connection_string)
    
    # Backup database if requested
    if args.backup and args.db_type == 'sqlite' and os.path.exists(args.db_path):
        backup_path = f"{args.db_path}.bak"
        logger.info(f"Creating backup of database: {backup_path}")
        import shutil
        shutil.copy2(args.db_path, backup_path)
    
    # Migrate data
    logger.info("Starting migration...")
    success = migrate_all_data(db_service)
    
    if success:
        logger.info("Migration completed successfully")
        return 0
    else:
        logger.error("Migration failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
