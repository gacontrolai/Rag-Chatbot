class BaseAppException(Exception):
    """Base exception for the application"""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseAppException):
    """Raised when input validation fails"""
    pass

class AuthenticationError(BaseAppException):
    """Raised when authentication fails"""
    pass

class PermissionError(BaseAppException):
    """Raised when user lacks permission for an action"""
    pass

class NotFoundError(BaseAppException):
    """Raised when a resource is not found"""
    pass

class ConflictError(BaseAppException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    pass

class RateLimitError(BaseAppException):
    """Raised when rate limit is exceeded"""
    pass

class FileError(BaseAppException):
    """Raised when file operations fail"""
    pass

def format_error_response(exception: BaseAppException, status_code: int = 400) -> tuple:
    """Format exception as API error response"""
    error_response = {
        'error': {
            'code': exception.code,
            'message': exception.message,
            'details': exception.details
        }
    }
    return error_response, status_code 