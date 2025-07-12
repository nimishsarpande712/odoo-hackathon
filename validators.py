import re
from typing import Dict, List, Tuple

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class UserValidator:
    """Comprehensive user input validation"""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate user name - only letters, spaces, hyphens, and apostrophes allowed
        Must be 2-50 characters long
        """
        if not name or not isinstance(name, str):
            return False, "Name is required"
        
        name = name.strip()
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Name must not exceed 50 characters"
        
        # Only allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for excessive spaces or special characters
        if re.search(r'\s{2,}', name):
            return False, "Name cannot contain multiple consecutive spaces"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format - must contain @ and proper domain
        """
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        email = email.strip().lower()
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Email must be in valid format (e.g., user@example.com)"
        
        # Check for common domains
        if not any(domain in email for domain in ['.com', '.org', '.net', '.edu', '.gov', '.in', '.co']):
            return False, "Email must contain a valid domain (e.g., .com, .org, .net)"
        
        if len(email) > 255:
            return False, "Email must not exceed 255 characters"
        
        return True, "Valid email"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength:
        - At least 8 characters long
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for number
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
        
        return True, "Valid password"
    
    @staticmethod
    def validate_location(location: str) -> Tuple[bool, str]:
        """
        Validate location - letters, spaces, commas, and common location characters
        """
        if not location:
            return True, "Location is optional"
        
        if not isinstance(location, str):
            return False, "Location must be text"
        
        location = location.strip()
        
        if len(location) > 255:
            return False, "Location must not exceed 255 characters"
        
        # Allow letters, spaces, commas, periods, hyphens, and parentheses
        if not re.match(r"^[a-zA-Z0-9\s,.\-()]+$", location):
            return False, "Location can only contain letters, numbers, spaces, commas, periods, hyphens, and parentheses"
        
        # Check for reasonable location format
        if len(location) < 2:
            return False, "Location must be at least 2 characters long"
        
        return True, "Valid location"
    
    @staticmethod
    def validate_skill_name(skill_name: str) -> Tuple[bool, str]:
        """
        Validate skill name - letters, spaces, and common skill-related characters
        """
        if not skill_name or not isinstance(skill_name, str):
            return False, "Skill name is required"
        
        skill_name = skill_name.strip()
        
        if len(skill_name) < 2:
            return False, "Skill name must be at least 2 characters long"
        
        if len(skill_name) > 100:
            return False, "Skill name must not exceed 100 characters"
        
        # Allow letters, numbers, spaces, hyphens, periods, and plus signs
        if not re.match(r"^[a-zA-Z0-9\s\-\.+#]+$", skill_name):
            return False, "Skill name can only contain letters, numbers, spaces, hyphens, periods, plus signs, and hash symbols"
        
        return True, "Valid skill name"
    
    @staticmethod
    def validate_proficiency_level(level: str) -> Tuple[bool, str]:
        """
        Validate proficiency level
        """
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        
        if not level or level not in valid_levels:
            return False, f"Proficiency level must be one of: {', '.join(valid_levels)}"
        
        return True, "Valid proficiency level"
    
    @staticmethod
    def validate_day(day: str) -> Tuple[bool, str]:
        """
        Validate day of the week
        """
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if not day or day not in valid_days:
            return False, f"Day must be one of: {', '.join(valid_days)}"
        
        return True, "Valid day"
    
    @staticmethod
    def validate_time_slot(time_slot: str) -> Tuple[bool, str]:
        """
        Validate time slot
        """
        valid_slots = ['Morning', 'Afternoon', 'Evening', 'Night']
        
        if not time_slot or time_slot not in valid_slots:
            return False, f"Time slot must be one of: {', '.join(valid_slots)}"
        
        return True, "Valid time slot"

def validate_user_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete user registration data
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate name
    is_valid, message = UserValidator.validate_name(data.get('name', ''))
    if not is_valid:
        errors.append(message)
    
    # Validate email
    is_valid, message = UserValidator.validate_email(data.get('email', ''))
    if not is_valid:
        errors.append(message)
    
    # Validate password
    is_valid, message = UserValidator.validate_password(data.get('password', ''))
    if not is_valid:
        errors.append(message)
    
    # Validate location (optional)
    if data.get('location'):
        is_valid, message = UserValidator.validate_location(data.get('location', ''))
        if not is_valid:
            errors.append(message)
    
    return len(errors) == 0, errors

def validate_availability_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate availability data
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate day
    day = data.get('day', '').strip()
    is_valid, message = UserValidator.validate_day(day)
    if not is_valid:
        errors.append(message)
    
    # Validate time_slot
    time_slot = data.get('time_slot', '').strip()
    is_valid, message = UserValidator.validate_time_slot(time_slot)
    if not is_valid:
        errors.append(message)
    
    return len(errors) == 0, errors
