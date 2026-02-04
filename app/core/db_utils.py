"""
Database utility functions and context managers.

Provides consistent database session handling with proper error management
and cleanup across all state classes.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional, TypeVar, Type, Any
import reflex as rx
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic cleanup.
    
    Ensures proper session lifecycle management:
    - Commits on success
    - Rolls back on error
    - Always closes session
    
    Usage:
        with get_db_session() as session:
            user = session.exec(select(User).where(User.id == user_id)).first()
            # ... do work with session
    
    Yields:
        A SQLModel Session instance
        
    Raises:
        SQLAlchemyError: On database errors
        
    Note:
        The commit happens AFTER the yield block completes successfully.
        If any exception occurs in the with block, it's caught here and rolled back.
    """
    with rx.session() as session:
        try:
            # Control passes to the with block here
            yield session
            # Execution resumes here only if with block completed successfully
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Unexpected error in database session: {str(e)}")
            raise


def safe_get_by_id(
    model_class: Type[T],
    record_id: int,
    session: Optional[Session] = None
) -> Optional[T]:
    """
    Safely fetch a record by ID with error handling.
    
    Args:
        model_class: The SQLModel class to query
        record_id: The ID of the record to fetch
        session: Optional existing session (creates new one if not provided)
        
    Returns:
        The model instance if found, None otherwise
        
    Usage:
        user = safe_get_by_id(User, user_id)
        if user:
            # Work with user
    """
    try:
        if session:
            return session.get(model_class, record_id)
        else:
            with get_db_session() as s:
                return s.get(model_class, record_id)
    except SQLAlchemyError as e:
        logger.error(
            f"Error fetching {model_class.__name__} with id {record_id}: {str(e)}"
        )
        return None
    except Exception as e:
        logger.exception(
            f"Unexpected error fetching {model_class.__name__} with id {record_id}: {str(e)}"
        )
        return None


def safe_query(
    statement,
    session: Optional[Session] = None,
    first: bool = False
) -> Optional[Any]:
    """
    Execute a query safely with error handling.
    
    Args:
        statement: The SQLModel select statement
        session: Optional existing session
        first: If True, return first result; otherwise return all results
        
    Returns:
        Query results or None on error
        
    Usage:
        stmt = select(User).where(User.email == email)
        user = safe_query(stmt, first=True)
    """
    try:
        if session:
            result = session.exec(statement)
            return result.first() if first else result.all()
        else:
            with get_db_session() as s:
                result = s.exec(statement)
                return result.first() if first else result.all()
    except SQLAlchemyError as e:
        logger.error(f"Database query error: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.exception(f"Unexpected error in query: {str(e)}")
        return None


def safe_add(
    instance,
    session: Optional[Session] = None,
    commit: bool = True
) -> bool:
    """
    Safely add a new instance to the database.
    
    Args:
        instance: The model instance to add
        session: Optional existing session
        commit: Whether to commit immediately
        
    Returns:
        True if successful, False otherwise
        
    Usage:
        new_user = User(email=email, username=username)
        if safe_add(new_user):
            # Success
    """
    try:
        if session:
            session.add(instance)
            if commit:
                session.commit()
            return True
        else:
            with get_db_session() as s:
                s.add(instance)
                if commit:
                    s.commit()
                return True
    except SQLAlchemyError as e:
        logger.error(f"Error adding {type(instance).__name__}: {str(e)}", exc_info=True)
        return False
    except Exception as e:
        logger.exception(f"Unexpected error adding {type(instance).__name__}: {str(e)}")
        return False


def safe_delete(
    instance,
    session: Optional[Session] = None,
    commit: bool = True
) -> bool:
    """
    Safely delete an instance from the database.
    
    Args:
        instance: The model instance to delete
        session: Optional existing session
        commit: Whether to commit immediately
        
    Returns:
        True if successful, False otherwise
        
    Usage:
        if safe_delete(user):
            # Success
    """
    try:
        if session:
            session.delete(instance)
            if commit:
                session.commit()
            return True
        else:
            with get_db_session() as s:
                s.delete(instance)
                if commit:
                    s.commit()
                return True
    except SQLAlchemyError as e:
        logger.error(f"Error deleting {type(instance).__name__}: {str(e)}", exc_info=True)
        return False
    except Exception as e:
        logger.exception(f"Unexpected error deleting {type(instance).__name__}: {str(e)}")
        return False
