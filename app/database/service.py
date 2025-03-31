"""
Database service for Caldera.

This module provides a service for managing database connections and repositories.
"""

import os
import logging
from typing import Dict, Any, Optional, Type, TypeVar, Union
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Base
from app.database.repositories import Repository, get_repository

T = TypeVar('T', bound=Base)

class DatabaseService:
    """
    Service for database operations.
    
    This service manages database connections and provides access to repositories.
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize the database service.
        
        Args:
            connection_string: Database connection string (SQLAlchemy format)
                If not provided, it will be constructed from environment variables
                or configuration.
        """
        self.logger = logging.getLogger('database_service')
        self.connection_string = connection_string or self._get_connection_string()
        self.engine = None
        self.session_factory = None
        self.Session = None
        self._initialize_engine()
    
    def _get_connection_string(self) -> str:
        """
        Get database connection string from environment variables or configuration.
        
        Returns:
            Database connection string
        """
        # Try to get connection string from environment variables
        db_type = os.environ.get('CALDERA_DB_TYPE', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = os.environ.get('CALDERA_DB_PATH', 'data/caldera.db')
            return f'sqlite:///{db_path}'
        elif db_type == 'postgresql':
            db_host = os.environ.get('CALDERA_DB_HOST', 'localhost')
            db_port = os.environ.get('CALDERA_DB_PORT', '5432')
            db_name = os.environ.get('CALDERA_DB_NAME', 'caldera')
            db_user = os.environ.get('CALDERA_DB_USER', 'caldera')
            db_password = os.environ.get('CALDERA_DB_PASSWORD', 'caldera')
            return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            # Default to SQLite in-memory database
            self.logger.warning(f"Unsupported database type: {db_type}. Using SQLite in-memory database.")
            return 'sqlite:///:memory:'
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine and session factory."""
        try:
            # Create engine with appropriate configuration
            if self.connection_string.startswith('sqlite'):
                # SQLite-specific configuration
                self.engine = create_engine(
                    self.connection_string,
                    connect_args={'check_same_thread': False},  # Allow multi-threaded access
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20
                )
            else:
                # Configuration for other databases
                self.engine = create_engine(
                    self.connection_string,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=1800  # Recycle connections after 30 minutes
                )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            self.logger.info(f"Database engine initialized with {self.connection_string}")
        except Exception as e:
            self.logger.error(f"Error initializing database engine: {e}")
            raise
    
    def create_tables(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Database tables created")
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables from the database."""
        try:
            Base.metadata.drop_all(self.engine)
            self.logger.info("Database tables dropped")
        except SQLAlchemyError as e:
            self.logger.error(f"Error dropping database tables: {e}")
            raise
    
    @contextmanager
    def session(self):
        """
        Provide a transactional scope around a series of operations.
        
        This context manager creates a session, yields it, and handles
        committing or rolling back the transaction.
        
        Yields:
            SQLAlchemy session
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_repository(self, model_class: Type[T]) -> Repository[T]:
        """
        Get repository for a model class.
        
        Args:
            model_class: Model class
            
        Returns:
            Repository for the model class
        """
        session = self.Session()
        return get_repository(session, model_class)
    
    async def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            with self.session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Database connection check failed: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """
    Get the database service singleton instance.
    
    Returns:
        Database service instance
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
