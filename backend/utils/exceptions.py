class NotFoundException(Exception):
    """Exception raised when a requested resource is not found."""
    pass

class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass

class AuthenticationError(Exception):
    """Exception raised when authentication fails."""
    pass

class AuthorizationError(Exception):
    """Exception raised when authorization fails."""
    pass

class DatabaseError(Exception):
    """Exception raised when database operations fail."""
    pass 