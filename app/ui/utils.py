"""
Utility functions for UI state management.

This module provides centralized error handling, logging, and notification
utilities for consistent behavior across all state classes.
"""

import logging
from typing import Optional, Callable, Any
from functools import wraps
import reflex as rx


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance for a module.
    
    Args:
        name: The name of the module (typically __name__)
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def handle_errors(
    user_message: str = "An error occurred. Please try again.",
    log_message: Optional[str] = None,
    return_value: Any = None
):
    """
    Decorator for consistent error handling in state event methods.
    
    Logs exceptions and displays user-friendly error messages via toast notifications.
    
    Args:
        user_message: The message to display to the user
        log_message: Optional custom message for logging (defaults to user_message)
        return_value: Value to return on error (default: None)
        
    Usage:
        @handle_errors("Failed to save project")
        @rx.event
        def save_project(self):
            # Your code here
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                msg = log_message or user_message
                logger.error(f"{msg}: {str(e)}", exc_info=True)
                # Set error message on first arg if it has the attribute (for state instances)
                if args and hasattr(args[0], 'error_message'):
                    args[0].error_message = user_message
                return rx.toast.error(user_message) if return_value is None else return_value
            except KeyError as e:
                msg = log_message or user_message
                logger.error(f"{msg} - Missing key: {str(e)}", exc_info=True)
                if args and hasattr(args[0], 'error_message'):
                    args[0].error_message = user_message
                return rx.toast.error(user_message) if return_value is None else return_value
            except ConnectionError as e:
                msg = log_message or "Database connection error"
                logger.error(f"{msg}: {str(e)}", exc_info=True)
                if args and hasattr(args[0], 'error_message'):
                    args[0].error_message = "Connection error. Please try again."
                return rx.toast.error("Connection error. Please try again.") if return_value is None else return_value
            except Exception as e:
                msg = log_message or user_message
                logger.exception(f"{msg}: {str(e)}")
                if args and hasattr(args[0], 'error_message'):
                    args[0].error_message = user_message
                return rx.toast.error(user_message) if return_value is None else return_value
        return wrapper
    return decorator


def notify_success(message: str) -> rx.Component:
    """
    Display a success notification to the user.
    
    Args:
        message: The success message to display
        
    Returns:
        A Reflex toast component
    """
    return rx.toast.success(message)


def notify_error(message: str) -> rx.Component:
    """
    Display an error notification to the user.
    
    Args:
        message: The error message to display
        
    Returns:
        A Reflex toast component
    """
    return rx.toast.error(message)


def notify_info(message: str) -> rx.Component:
    """
    Display an info notification to the user.
    
    Args:
        message: The info message to display
        
    Returns:
        A Reflex toast component
    """
    return rx.toast.info(message)


def notify_warning(message: str) -> rx.Component:
    """
    Display a warning notification to the user.
    
    Args:
        message: The warning message to display
        
    Returns:
        A Reflex toast component
    """
    return rx.toast.warning(message)
