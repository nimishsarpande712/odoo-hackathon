import logging
import traceback
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, request
import mysql.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('skill_swap.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorCodes:
    """Standardized error codes for the application"""
    
    # Authentication & Authorization
    INVALID_CREDENTIALS = 'AUTH_001'
    ACCOUNT_LOCKED = 'AUTH_002'
    EMAIL_NOT_VERIFIED = 'AUTH_003'
    TOKEN_EXPIRED = 'AUTH_004'
    TOKEN_INVALID = 'AUTH_005'
    UNAUTHORIZED = 'AUTH_006'
    
    # Validation
    VALIDATION_ERROR = 'VAL_001'
    EMAIL_INVALID = 'VAL_002'
    PASSWORD_WEAK = 'VAL_003'
    REQUIRED_FIELD = 'VAL_004'
    
    # Database
    DB_CONNECTION_ERROR = 'DB_001'
    DB_QUERY_ERROR = 'DB_002'
    DUPLICATE_ENTRY = 'DB_003'
    RECORD_NOT_FOUND = 'DB_004'
    
    # Email
    EMAIL_SEND_FAILED = 'EMAIL_001'
    SMTP_ERROR = 'EMAIL_002'
    TEMPLATE_ERROR = 'EMAIL_003'
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = 'RATE_001'
    TOO_MANY_ATTEMPTS = 'RATE_002'
    
    # Server Errors
    INTERNAL_ERROR = 'SRV_001'
    SERVICE_UNAVAILABLE = 'SRV_002'
    CONFIGURATION_ERROR = 'SRV_003'

class SkillSwapException(Exception):
    """Base exception class for SkillSwap application"""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 400, details: Dict = None):
        self.message = message
        self.error_code = error_code or ErrorCodes.INTERNAL_ERROR
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        return {
            'error': True,
            'message': self.message,
            'error_code': self.error_code,
            'timestamp': self.timestamp,
            'details': self.details
        }

class ValidationException(SkillSwapException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, validation_errors: Dict = None):
        details = {'field': field} if field else {}
        if validation_errors:
            details['validation_errors'] = validation_errors
        super().__init__(message, ErrorCodes.VALIDATION_ERROR, 400, details)

class AuthenticationException(SkillSwapException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str, error_code: str = ErrorCodes.INVALID_CREDENTIALS):
        super().__init__(message, error_code, 401)

class DatabaseException(SkillSwapException):
    """Exception for database errors"""
    
    def __init__(self, message: str, error_code: str = ErrorCodes.DB_QUERY_ERROR, original_error: Exception = None):
        details = {}
        if original_error:
            details['original_error'] = str(original_error)
        super().__init__(message, error_code, 500, details)

class EmailException(SkillSwapException):
    """Exception for email service errors"""
    
    def __init__(self, message: str, error_code: str = ErrorCodes.EMAIL_SEND_FAILED):
        super().__init__(message, error_code, 500)

class RateLimitException(SkillSwapException):
    """Exception for rate limiting"""
    
    def __init__(self, message: str, retry_after: int = None):
        details = {'retry_after': retry_after} if retry_after else {}
        super().__init__(message, ErrorCodes.RATE_LIMIT_EXCEEDED, 429, details)

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def log_error(error: Exception, context: Dict = None):
        """Log error with context information"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        if hasattr(request, 'remote_addr'):
            error_info['ip_address'] = request.remote_addr
        if hasattr(request, 'user_agent'):
            error_info['user_agent'] = str(request.user_agent)
        if hasattr(request, 'endpoint'):
            error_info['endpoint'] = request.endpoint
        
        logger.error(f"Application Error: {error_info}")
    
    @staticmethod
    def handle_database_error(error: mysql.connector.Error, operation: str = "Database operation") -> DatabaseException:
        """Convert MySQL errors to application exceptions"""
        error_msg = str(error)
        
        if "Duplicate entry" in error_msg:
            if "email" in error_msg.lower():
                return DatabaseException(
                    "Email address is already registered",
                    ErrorCodes.DUPLICATE_ENTRY
                )
            return DatabaseException(
                "Record already exists",
                ErrorCodes.DUPLICATE_ENTRY
            )
        
        elif error.errno == 1045:  # Access denied
            return DatabaseException(
                "Database authentication failed",
                ErrorCodes.DB_CONNECTION_ERROR
            )
        
        elif error.errno == 2003:  # Can't connect
            return DatabaseException(
                "Database connection failed",
                ErrorCodes.DB_CONNECTION_ERROR
            )
        
        elif error.errno == 1146:  # Table doesn't exist
            return DatabaseException(
                "Database schema error",
                ErrorCodes.DB_QUERY_ERROR
            )
        
        else:
            return DatabaseException(
                f"{operation} failed",
                ErrorCodes.DB_QUERY_ERROR,
                error
            )
    
    @staticmethod
    def create_error_response(error: Exception, include_details: bool = False) -> Tuple[Dict, int]:
        """Create standardized error response"""
        if isinstance(error, SkillSwapException):
            response_data = error.to_dict()
            status_code = error.status_code
        else:
            # Handle unexpected errors
            ErrorHandler.log_error(error)
            response_data = {
                'error': True,
                'message': 'An unexpected error occurred',
                'error_code': ErrorCodes.INTERNAL_ERROR,
                'timestamp': datetime.utcnow().isoformat()
            }
            status_code = 500
        
        # Include details only in development mode or for certain error types
        if not include_details and 'details' in response_data:
            if not isinstance(error, ValidationException):
                response_data.pop('details', None)
        
        return response_data, status_code

def handle_errors(include_details: bool = False):
    """Decorator for handling errors in Flask routes"""
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SkillSwapException as e:
                response_data, status_code = ErrorHandler.create_error_response(e, include_details)
                return jsonify(response_data), status_code
            except mysql.connector.Error as e:
                db_error = ErrorHandler.handle_database_error(e)
                response_data, status_code = ErrorHandler.create_error_response(db_error, include_details)
                return jsonify(response_data), status_code
            except Exception as e:
                ErrorHandler.log_error(e, {'function': f.__name__})
                response_data, status_code = ErrorHandler.create_error_response(e, include_details)
                return jsonify(response_data), status_code
        
        return wrapper
    return decorator

def log_user_action(user_id: Optional[int], action: str, details: Dict = None):
    """Log user actions for security and debugging"""
    log_data = {
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': getattr(request, 'remote_addr', None),
        'user_agent': str(getattr(request, 'user_agent', '')),
        'details': details or {}
    }
    
    logger.info(f"User Action: {log_data}")

def validate_request_data(required_fields: list, optional_fields: list = None) -> Dict:
    """Validate and extract request data"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationException("Request body must be valid JSON")
        
        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationException(
                f"Missing required fields: {', '.join(missing_fields)}",
                validation_errors={'missing_fields': missing_fields}
            )
        
        # Extract and clean data
        result = {}
        all_fields = required_fields + (optional_fields or [])
        
        for field in all_fields:
            if field in data:
                value = data[field]
                # Clean string values
                if isinstance(value, str):
                    value = value.strip()
                result[field] = value
        
        return result
        
    except Exception as e:
        if isinstance(e, ValidationException):
            raise
        raise ValidationException("Invalid request data format")

# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.attempts = {}
    
    def is_rate_limited(self, key: str, max_attempts: int, window_minutes: int) -> Tuple[bool, int]:
        """Check if key is rate limited"""
        now = datetime.utcnow()
        window_start = now.timestamp() - (window_minutes * 60)
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Clean old attempts
        self.attempts[key] = [
            attempt for attempt in self.attempts[key] 
            if attempt > window_start
        ]
        
        current_attempts = len(self.attempts[key])
        
        if current_attempts >= max_attempts:
            # Calculate retry after time
            oldest_attempt = min(self.attempts[key])
            retry_after = int((oldest_attempt + (window_minutes * 60)) - now.timestamp())
            return True, max(retry_after, 1)
        
        return False, 0
    
    def record_attempt(self, key: str):
        """Record an attempt for the key"""
        now = datetime.utcnow().timestamp()
        if key not in self.attempts:
            self.attempts[key] = []
        self.attempts[key].append(now)

# Global rate limiter instance
rate_limiter = RateLimiter()
