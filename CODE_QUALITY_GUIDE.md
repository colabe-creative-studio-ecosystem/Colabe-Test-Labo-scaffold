# Code Quality Improvements Guide

This document describes the systematic improvements made to the Colabe Test Labo codebase and provides guidelines for maintaining code quality across all files.

## Overview

We have implemented comprehensive improvements across all 107 files in the repository to enhance:
- **Logging**: Consistent logging across all state files
- **Error Handling**: Standardized error handling with user-friendly notifications
- **Database Operations**: Safe database session management
- **Documentation**: Comprehensive docstrings and type hints

## New Utilities

### 1. Error Handling and Notifications (`app/ui/utils.py`)

#### get_logger(name: str)
Get a configured logger instance for any module.

```python
from app.ui.utils import get_logger

logger = get_logger(__name__)
logger.info("Operation started")
logger.error("Operation failed", exc_info=True)
```

#### Notification Functions
Display user-friendly messages:

```python
from app.ui.utils import notify_success, notify_error, notify_warning, notify_info

# In your event handlers
return notify_success("Project created successfully!")
return notify_error("Failed to create project.")
return notify_warning("Please select a project first.")
return notify_info("Loading data...")
```

#### handle_errors Decorator
Automatically handle exceptions in event methods:

```python
from app.ui.utils import handle_errors

@handle_errors("Failed to save project")
@rx.event
def save_project(self):
    # Your code here
    # Exceptions are automatically caught and logged
    # User sees friendly error message
```

### 2. Database Utilities (`app/core/db_utils.py`)

#### get_db_session()
Context manager for safe database operations:

```python
from app.core.db_utils import get_db_session

with get_db_session() as session:
    user = session.get(User, user_id)
    user.name = "Updated Name"
    # Automatically commits on success, rolls back on error
```

#### Safe Query Functions

```python
from app.core.db_utils import safe_get_by_id, safe_query, safe_add, safe_delete

# Get by ID with error handling
user = safe_get_by_id(User, user_id)

# Execute query safely
stmt = select(User).where(User.email == email)
user = safe_query(stmt, first=True)

# Add new record
new_user = User(email=email, username=username)
if safe_add(new_user):
    logger.info("User created successfully")

# Delete record
if safe_delete(user):
    logger.info("User deleted successfully")
```

## Best Practices

### Logging Standards

1. **Always import and create a logger** at the module level:
```python
from app.ui.utils import get_logger

logger = get_logger(__name__)
```

2. **Use appropriate log levels**:
   - `logger.debug()` - Detailed diagnostic information
   - `logger.info()` - General informational messages
   - `logger.warning()` - Warning messages for recoverable issues
   - `logger.error()` - Error messages for failures
   - `logger.exception()` - Error messages with full stack trace

3. **Log examples**:
```python
# Info level - successful operations
logger.info(f"User {username} logged in successfully")
logger.info(f"Loaded {len(projects)} projects")

# Warning level - unexpected but handled situations
logger.warning(f"Attempted to delete non-existent project {project_id}")

# Error level - failures that need attention
logger.error(f"Failed to connect to Stripe API: {str(e)}")

# Exception level - failures with stack traces
logger.exception(f"Unexpected error in registration: {str(e)}")
```

### Error Handling Standards

1. **Always use specific exception types** instead of bare `except Exception`:
```python
# Good
try:
    value = int(data["id"])
except KeyError as e:
    logger.error(f"Missing required field: {str(e)}")
    return notify_error("Invalid form data.")
except ValueError as e:
    logger.error(f"Invalid ID format: {str(e)}")
    return notify_error("Invalid ID provided.")
except Exception as e:
    logger.exception(f"Unexpected error: {str(e)}")
    return notify_error("An error occurred. Please try again.")

# Bad
try:
    value = int(data["id"])
except Exception as e:
    return notify_error("Error occurred.")
```

2. **Always notify users of errors**:
```python
@rx.event
async def save_data(self):
    try:
        # ... operations
        return notify_success("Data saved successfully!")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return notify_error("Invalid data provided.")
    except Exception as e:
        logger.exception(f"Error saving data: {str(e)}")
        return notify_error("Failed to save data. Please try again.")
```

### Documentation Standards

1. **Add docstrings to all classes**:
```python
class ProjectState(rx.State):
    """
    Project management state.
    
    Handles creation, viewing, editing, and deletion of projects
    with multi-tenant isolation.
    """
```

2. **Add docstrings to all public methods**:
```python
@rx.event
async def create_project(self, name: str):
    """
    Create a new project for the current tenant.
    
    Args:
        name: The name of the project
        
    Returns:
        Notification toast with success/error message
    """
```

3. **Add docstrings to complex helper methods**:
```python
def _calculate_metrics(self, data: list) -> dict:
    """
    Calculate aggregated metrics from raw data.
    
    Args:
        data: List of data points
        
    Returns:
        Dictionary containing calculated metrics
    """
```

### Type Hints Standards

1. **Always add type hints to function parameters and return values**:
```python
def process_data(self, data: dict) -> bool:
    """Process incoming data."""
    pass

async def load_user(self, user_id: int) -> Optional[User]:
    """Load user by ID."""
    pass
```

2. **Use proper types for complex structures**:
```python
from typing import List, Dict, Optional, Tuple

def get_stats(self) -> Dict[str, int]:
    return {"total": 10, "active": 5}

def get_users(self) -> List[User]:
    return []
```

## State File Template

Use this template when creating new state files:

```python
import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import YourModel
from app.ui.utils import get_logger, notify_error, notify_success
from app.core.db_utils import get_db_session, safe_get_by_id

logger = get_logger(__name__)


class YourDisplayModel(rx.Base):
    """Display model for your data."""
    id: int
    name: str


class YourState(rx.State):
    """
    Brief description of what this state manages.
    
    Detailed explanation of the functionality,
    including any important notes about usage.
    """
    items: list[YourDisplayModel] = []
    error_message: str = ""

    @rx.event
    async def load_data(self):
        """Load data for the current tenant."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                logger.warning("Attempted to load data without authentication")
                return
                
            with get_db_session() as session:
                items = session.exec(
                    sqlmodel.select(YourModel).where(
                        YourModel.tenant_id == auth_state.user.tenant_id
                    )
                ).all()
                
                self.items = [
                    YourDisplayModel(
                        id=item.id,
                        name=item.name
                    )
                    for item in items
                ]
                
                logger.info(f"Loaded {len(self.items)} items")
                
        except Exception as e:
            logger.exception(f"Error loading data: {str(e)}")
            return notify_error("Failed to load data.")

    @rx.event
    async def create_item(self, name: str):
        """
        Create a new item.
        
        Args:
            name: The name of the item
        """
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                return notify_error("Please log in.")
                
            if not name:
                return notify_error("Name is required.")
                
            with get_db_session() as session:
                item = YourModel(
                    name=name,
                    tenant_id=auth_state.user.tenant_id
                )
                session.add(item)
                session.commit()
                
            logger.info(f"Created item: {name}")
            await self.load_data()
            return notify_success("Item created successfully!")
            
        except Exception as e:
            logger.exception(f"Error creating item: {str(e)}")
            return notify_error("Failed to create item.")
```

## Migration Guide

### Updating Existing State Files

1. **Add imports**:
```python
from app.ui.utils import get_logger, notify_error, notify_success, notify_warning
logger = get_logger(__name__)
```

2. **Add class docstring**:
```python
class YourState(rx.State):
    """
    Brief description of the state's purpose.
    """
```

3. **Add error handling to event methods**:
```python
@rx.event
async def your_method(self):
    try:
        # existing code
        logger.info("Operation successful")
        return notify_success("Success!")
    except SpecificError as e:
        logger.error(f"Specific error: {str(e)}")
        return notify_error("User-friendly message.")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return notify_error("An error occurred.")
```

4. **Add method docstrings**:
```python
@rx.event
async def your_method(self):
    """
    Brief description of what the method does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
```

### Updating Existing Database Code

Replace bare `rx.session()` usage with safe utilities:

**Before:**
```python
with rx.session() as session:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
```

**After:**
```python
from app.core.db_utils import safe_get_by_id, safe_delete

user = safe_get_by_id(User, user_id)
if user and safe_delete(user):
    logger.info(f"Deleted user {user_id}")
```

## Testing

When testing your changes:

1. **Verify logging output**:
   - Check that log messages appear in the console
   - Verify log levels are appropriate
   - Ensure sensitive data is not logged

2. **Test error scenarios**:
   - Trigger errors intentionally
   - Verify user sees friendly error messages
   - Check that errors are logged with context

3. **Test database operations**:
   - Verify transactions commit properly
   - Test rollback on errors
   - Check for resource leaks

## Summary

These improvements provide:
- ✅ **Better Debugging**: Comprehensive logging helps diagnose issues quickly
- ✅ **User Experience**: Friendly error messages instead of silent failures
- ✅ **Maintainability**: Consistent patterns make code easier to understand
- ✅ **Reliability**: Proper error handling prevents crashes
- ✅ **Safety**: Database utilities prevent resource leaks and data corruption

By following these guidelines, all 107 files in the repository will maintain consistent high quality.
