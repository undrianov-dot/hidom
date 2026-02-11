"""Error handling for HiDOM."""
import logging
from functools import wraps
from typing import Type, Tuple

_LOGGER = logging.getLogger(__name__)

class HiDOMError(Exception):
    """Base exception for HiDOM integration."""
    pass

class ConnectionError(HiDOMError):
    """Connection related errors."""
    pass

class DeviceError(HiDOMError):
    """Device specific errors."""
    pass

def handle_errors(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    default_return=None
):
    """Decorator for error handling."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                _LOGGER.error(
                    "Error in %s: %s",
                    func.__name__,
                    str(e)
                )
                return default_return
        return wrapper
    return decorator

class ErrorHandler:
    """Centralized error handler."""
    
    @staticmethod
    def log_and_continue(func):
        """Log error and continue execution."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                _LOGGER.warning(
                    "Non-critical error in %s: %s",
                    func.__name__,
                    str(e)
                )
                return None
        return wrapper