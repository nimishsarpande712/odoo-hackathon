import bcrypt
import mysql.connector
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from email_service import email_service
from error_handling import (
    AuthenticationException, DatabaseException, EmailException, ValidationException,
    ErrorCodes, log_user_action, rate_limiter, RateLimitException
)
from validators import UserValidator

class AuthService:
    """Authentication service with email verification and password reset"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as e:
            raise DatabaseException("Failed to connect to database", ErrorCodes.DB_CONNECTION_ERROR, e)
    
    def log_email_attempt(self, user_id: Optional[int], email: str, email_type: str, 
                         subject: str, status: str, error_msg: str = None) -> None:
        """Log email sending attempt"""
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO email_logs (user_id, email_address, email_type, subject, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, email_type, subject, status, error_msg))
            db.commit()
            cursor.close()
            db.close()
        except Exception as e:
            # Don't let email logging errors break the main flow
            print(f"Failed to log email attempt: {e}")
    
    def cleanup_expired_tokens(self, user_id: int) -> None:
        """Clean up expired tokens for a user"""
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            now = datetime.utcnow()
            
            # Clean up expired email verification tokens
            cursor.execute("""
                DELETE FROM email_verification_tokens 
                WHERE user_id = %s AND expires_at < %s
            """, (user_id, now))
            
            # Clean up expired password reset tokens
            cursor.execute("""
                DELETE FROM password_reset_tokens 
                WHERE user_id = %s AND expires_at < %s
            """, (user_id, now))
            
            db.commit()
            cursor.close()
            db.close()
        except Exception as e:
            # Don't let cleanup errors break the main flow
            print(f"Failed to cleanup expired tokens: {e}")
    
    def check_account_locked(self, user_id: int) -> Tuple[bool, Optional[datetime]]:
        """Check if account is locked and return lock status"""
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT account_locked_until, login_attempts 
                FROM users WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            db.close()
            
            if result:
                locked_until, login_attempts = result
                if locked_until and locked_until > datetime.utcnow():
                    return True, locked_until
                elif login_attempts >= 5:  # Max attempts reached
                    return True, None
            
            return False, None
            
        except mysql.connector.Error as e:
            raise DatabaseException("Failed to check account lock status", original_error=e)
    
    def update_login_attempts(self, user_id: int, success: bool, ip_address: str = None) -> None:
        """Update login attempts counter"""
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            if success:
                # Reset attempts on successful login
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = 0, account_locked_until = NULL 
                    WHERE id = %s
                """, (user_id,))
                log_user_action(user_id, "login_success", {"ip_address": ip_address})
            else:
                # Increment attempts and potentially lock account
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = login_attempts + 1,
                        account_locked_until = CASE 
                            WHEN login_attempts + 1 >= 5 THEN %s
                            ELSE account_locked_until 
                        END
                    WHERE id = %s
                """, (datetime.utcnow() + timedelta(minutes=30), user_id))
                log_user_action(user_id, "login_failed", {"ip_address": ip_address})
            
            db.commit()
            cursor.close()
            db.close()
            
        except mysql.connector.Error as e:
            raise DatabaseException("Failed to update login attempts", original_error=e)
    
    def register_user(self, user_data: Dict[str, Any], ip_address: str = None) -> Tuple[bool, str, Optional[int]]:
        """Register a new user with email verification"""
        
        # Validate user data
        is_valid, validation_errors = self.validate_registration_data(user_data)
        if not is_valid:
            raise ValidationException("Registration validation failed", validation_errors=validation_errors)
        
        # Hash password
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (user_data['email'],))
            if cursor.fetchone():
                cursor.close()
                db.close()
                raise ValidationException("Email address is already registered")
            
            # Insert new user (email_verified = False by default)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, location, is_public, email_verified) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_data['name'], 
                user_data['email'], 
                password_hash, 
                user_data.get('location'), 
                user_data.get('is_public', True),
                False  # Email not verified initially
            ))
            
            user_id = cursor.lastrowid
            
            # Generate verification token
            verification_token = email_service.generate_secure_token()
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Store verification token
            cursor.execute("""
                INSERT INTO email_verification_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user_id, verification_token, expires_at))
            
            # Also update user table for backward compatibility
            cursor.execute("""
                UPDATE users 
                SET email_verification_token = %s, email_verification_expires = %s
                WHERE id = %s
            """, (verification_token, expires_at, user_id))
            
            db.commit()
            cursor.close()
            db.close()
            
            # Send verification email
            try:
                success, message = email_service.send_verification_email(
                    user_data['email'], 
                    user_data['name'], 
                    verification_token
                )
                
                if success:
                    self.log_email_attempt(user_id, user_data['email'], 'verification', 
                                         'Verify your SkillSwap account', 'sent')
                    log_user_action(user_id, "user_registered", {
                        "email": user_data['email'], 
                        "ip_address": ip_address
                    })
                    return True, "Registration successful! Please check your email to verify your account.", user_id
                else:
                    self.log_email_attempt(user_id, user_data['email'], 'verification', 
                                         'Verify your SkillSwap account', 'failed', message)
                    return True, "Registration successful! However, we couldn't send the verification email. Please request a new one.", user_id
                    
            except Exception as e:
                self.log_email_attempt(user_id, user_data['email'], 'verification', 
                                     'Verify your SkillSwap account', 'failed', str(e))
                return True, "Registration successful! However, we couldn't send the verification email. Please request a new one.", user_id
            
        except mysql.connector.Error as e:
            raise DatabaseException("Registration failed", original_error=e)
    
    def validate_registration_data(self, user_data: Dict[str, Any]) -> Tuple[bool, Dict]:
        """Validate registration data"""
        errors = {}
        
        # Validate name
        if not user_data.get('name'):
            errors['name'] = "Name is required"
        else:
            is_valid, message = UserValidator.validate_name(user_data['name'])
            if not is_valid:
                errors['name'] = message
        
        # Validate email
        if not user_data.get('email'):
            errors['email'] = "Email is required"
        else:
            is_valid, message = UserValidator.validate_email(user_data['email'])
            if not is_valid:
                errors['email'] = message
        
        # Validate password
        if not user_data.get('password'):
            errors['password'] = "Password is required"
        else:
            is_valid, message = UserValidator.validate_password(user_data['password'])
            if not is_valid:
                errors['password'] = message
        
        # Validate location if provided
        if user_data.get('location'):
            is_valid, message = UserValidator.validate_location(user_data['location'])
            if not is_valid:
                errors['location'] = message
        
        return len(errors) == 0, errors
    
    def login_user(self, username: str, password: str, ip_address: str = None) -> Tuple[Dict[str, Any], str]:
        """Login user with enhanced security"""
        
        # Rate limiting
        rate_key = f"login_{ip_address or 'unknown'}"
        is_limited, retry_after = rate_limiter.is_rate_limited(rate_key, 10, 15)  # 10 attempts per 15 minutes
        if is_limited:
            raise RateLimitException(
                f"Too many login attempts. Try again in {retry_after} seconds.",
                retry_after
            )
        
        # Record login attempt
        rate_limiter.record_attempt(rate_key)
        
        # Validate input
        if not username or not password:
            raise ValidationException("Username and password are required")
        
        # Determine if username is email
        is_email = '@' in username
        if is_email:
            is_valid, message = UserValidator.validate_email(username)
            if not is_valid:
                raise ValidationException("Invalid email format")
        else:
            is_valid, message = UserValidator.validate_name(username)
            if not is_valid:
                raise ValidationException("Invalid username format")
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Get user data
            if is_email:
                cursor.execute("""
                    SELECT id, name, email, password_hash, email_verified, 
                           login_attempts, account_locked_until
                    FROM users WHERE email = %s
                """, (username.lower(),))
            else:
                cursor.execute("""
                    SELECT id, name, email, password_hash, email_verified, 
                           login_attempts, account_locked_until
                    FROM users WHERE name = %s
                """, (username,))
            
            result = cursor.fetchone()
            cursor.close()
            db.close()
            
            if not result:
                log_user_action(None, "login_failed", {
                    "username": username, 
                    "reason": "user_not_found", 
                    "ip_address": ip_address
                })
                raise AuthenticationException("Invalid credentials")
            
            user_id, name, email, stored_password, email_verified, login_attempts, locked_until = result
            
            # Check if account is locked
            is_locked, lock_time = self.check_account_locked(user_id)
            if is_locked:
                if lock_time:
                    minutes_left = int((lock_time - datetime.utcnow()).total_seconds() / 60)
                    raise AuthenticationException(
                        f"Account temporarily locked. Try again in {minutes_left} minutes.",
                        ErrorCodes.ACCOUNT_LOCKED
                    )
                else:
                    raise AuthenticationException(
                        "Account locked due to too many failed attempts. Please reset your password.",
                        ErrorCodes.ACCOUNT_LOCKED
                    )
            
            # Verify password
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
                self.update_login_attempts(user_id, False, ip_address)
                raise AuthenticationException("Invalid credentials")
            
            # Check if email is verified - SKIP VERIFICATION REQUIREMENT
            # if not email_verified:
            #     log_user_action(user_id, "login_attempted_unverified", {"ip_address": ip_address})
            #     raise AuthenticationException(
            #         "Please verify your email address before logging in. Check your inbox for the verification link.",
            #         ErrorCodes.EMAIL_NOT_VERIFIED
            #     )
            
            # Successful login
            self.update_login_attempts(user_id, True, ip_address)
            
            return {
                'user_id': user_id,
                'name': name,
                'email': email,
                'email_verified': email_verified
            }, "Login successful"
            
        except mysql.connector.Error as e:
            raise DatabaseException("Login failed due to database error", original_error=e)
    
    def verify_email(self, token: str, ip_address: str = None) -> Tuple[bool, str]:
        """Verify email address using token"""
        if not token:
            raise ValidationException("Verification token is required")
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Check token in the tokens table
            cursor.execute("""
                SELECT evt.user_id, evt.expires_at, evt.is_used, u.name, u.email
                FROM email_verification_tokens evt
                JOIN users u ON evt.user_id = u.id
                WHERE evt.token = %s AND evt.is_used = FALSE
            """, (token,))
            
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                db.close()
                raise AuthenticationException("Invalid or expired verification token", ErrorCodes.TOKEN_INVALID)
            
            user_id, expires_at, is_used, user_name, email = result
            
            # Check if token has expired
            if expires_at < datetime.utcnow():
                cursor.close()
                db.close()
                raise AuthenticationException("Verification token has expired", ErrorCodes.TOKEN_EXPIRED)
            
            # Mark token as used
            cursor.execute("""
                UPDATE email_verification_tokens 
                SET is_used = TRUE, used_at = %s 
                WHERE token = %s
            """, (datetime.utcnow(), token))
            
            # Update user email verification status
            cursor.execute("""
                UPDATE users 
                SET email_verified = TRUE, 
                    email_verification_token = NULL, 
                    email_verification_expires = NULL,
                    login_attempts = 0,
                    account_locked_until = NULL
                WHERE id = %s
            """, (user_id,))
            
            db.commit()
            cursor.close()
            db.close()
            
            log_user_action(user_id, "email_verified", {
                "email": email,
                "ip_address": ip_address
            })
            
            return True, f"Email verification successful! Welcome to SkillSwap, {user_name}!"
            
        except mysql.connector.Error as e:
            raise DatabaseException("Email verification failed", original_error=e)
    
    def request_password_reset(self, email: str, ip_address: str = None, user_agent: str = None) -> Tuple[bool, str]:
        """Request password reset"""
        
        # Validate email
        is_valid, message = UserValidator.validate_email(email)
        if not is_valid:
            raise ValidationException("Invalid email format")
        
        # Rate limiting
        rate_key = f"password_reset_{email}"
        is_limited, retry_after = rate_limiter.is_rate_limited(rate_key, 3, 60)  # 3 attempts per hour
        if is_limited:
            raise RateLimitException(
                f"Too many password reset requests. Try again in {retry_after // 60} minutes.",
                retry_after
            )
        
        rate_limiter.record_attempt(rate_key)
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id, name, email_verified FROM users WHERE email = %s", (email.lower(),))
            result = cursor.fetchone()
            
            if not result:
                # Don't reveal if email exists or not for security
                log_user_action(None, "password_reset_requested_invalid_email", {
                    "email": email,
                    "ip_address": ip_address
                })
                return True, "If an account with this email exists, you will receive password reset instructions."
            
            user_id, user_name, email_verified = result
            
            # Only allow password reset for verified emails
            if not email_verified:
                log_user_action(user_id, "password_reset_requested_unverified", {
                    "email": email,
                    "ip_address": ip_address
                })
                raise AuthenticationException(
                    "Please verify your email address first before requesting a password reset.",
                    ErrorCodes.EMAIL_NOT_VERIFIED
                )
            
            # Clean up old tokens
            self.cleanup_expired_tokens(user_id)
            
            # Generate reset token
            reset_token = email_service.generate_secure_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
            
            # Store reset token
            cursor.execute("""
                INSERT INTO password_reset_tokens 
                (user_id, token, expires_at, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, reset_token, expires_at, ip_address, user_agent))
            
            # Also update user table for backward compatibility
            cursor.execute("""
                UPDATE users 
                SET password_reset_token = %s, password_reset_expires = %s
                WHERE id = %s
            """, (reset_token, expires_at, user_id))
            
            db.commit()
            cursor.close()
            db.close()
            
            # Send reset email
            try:
                success, message = email_service.send_password_reset_email(email, user_name, reset_token)
                
                if success:
                    self.log_email_attempt(user_id, email, 'password_reset', 
                                         'Reset your SkillSwap password', 'sent')
                    log_user_action(user_id, "password_reset_requested", {
                        "email": email,
                        "ip_address": ip_address
                    })
                    return True, "Password reset instructions have been sent to your email."
                else:
                    self.log_email_attempt(user_id, email, 'password_reset', 
                                         'Reset your SkillSwap password', 'failed', message)
                    raise EmailException("Failed to send password reset email")
                    
            except Exception as e:
                self.log_email_attempt(user_id, email, 'password_reset', 
                                     'Reset your SkillSwap password', 'failed', str(e))
                raise EmailException("Failed to send password reset email")
            
        except mysql.connector.Error as e:
            raise DatabaseException("Password reset request failed", original_error=e)
    
    def reset_password(self, token: str, new_password: str, ip_address: str = None) -> Tuple[bool, str]:
        """Reset password using token"""
        
        if not token:
            raise ValidationException("Reset token is required")
        
        # Validate new password
        is_valid, message = UserValidator.validate_password(new_password)
        if not is_valid:
            raise ValidationException(f"Invalid password: {message}")
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Check token
            cursor.execute("""
                SELECT prt.user_id, prt.expires_at, prt.is_used, u.name, u.email
                FROM password_reset_tokens prt
                JOIN users u ON prt.user_id = u.id
                WHERE prt.token = %s AND prt.is_used = FALSE
            """, (token,))
            
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                db.close()
                raise AuthenticationException("Invalid or expired reset token", ErrorCodes.TOKEN_INVALID)
            
            user_id, expires_at, is_used, user_name, email = result
            
            # Check if token has expired
            if expires_at < datetime.utcnow():
                cursor.close()
                db.close()
                raise AuthenticationException("Reset token has expired", ErrorCodes.TOKEN_EXPIRED)
            
            # Hash new password
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Mark token as used
            cursor.execute("""
                UPDATE password_reset_tokens 
                SET is_used = TRUE, used_at = %s 
                WHERE token = %s
            """, (datetime.utcnow(), token))
            
            # Update user password and reset security fields
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, 
                    password_reset_token = NULL, 
                    password_reset_expires = NULL,
                    login_attempts = 0,
                    account_locked_until = NULL
                WHERE id = %s
            """, (password_hash, user_id))
            
            db.commit()
            cursor.close()
            db.close()
            
            log_user_action(user_id, "password_reset", {
                "email": email,
                "ip_address": ip_address
            })
            
            return True, "Password reset successful! You can now login with your new password."
            
        except mysql.connector.Error as e:
            raise DatabaseException("Password reset failed", original_error=e)
    
    def resend_verification_email(self, email: str, ip_address: str = None) -> Tuple[bool, str]:
        """Resend email verification"""
        
        # Validate email
        is_valid, message = UserValidator.validate_email(email)
        if not is_valid:
            raise ValidationException("Invalid email format")
        
        # Rate limiting
        rate_key = f"verify_resend_{email}"
        is_limited, retry_after = rate_limiter.is_rate_limited(rate_key, 3, 15)  # 3 attempts per 15 minutes
        if is_limited:
            raise RateLimitException(
                f"Too many verification requests. Try again in {retry_after} seconds.",
                retry_after
            )
        
        rate_limiter.record_attempt(rate_key)
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            
            # Check if user exists and is not verified
            cursor.execute("""
                SELECT id, name, email_verified 
                FROM users WHERE email = %s
            """, (email.lower(),))
            
            result = cursor.fetchone()
            
            if not result:
                # Don't reveal if email exists or not
                return True, "If an account with this email exists and is not verified, you will receive a verification email."
            
            user_id, user_name, email_verified = result
            
            if email_verified:
                return True, "This email address is already verified."
            
            # Clean up old tokens
            self.cleanup_expired_tokens(user_id)
            
            # Generate new verification token
            verification_token = email_service.generate_secure_token()
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Store new verification token
            cursor.execute("""
                INSERT INTO email_verification_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user_id, verification_token, expires_at))
            
            # Update user table
            cursor.execute("""
                UPDATE users 
                SET email_verification_token = %s, email_verification_expires = %s
                WHERE id = %s
            """, (verification_token, expires_at, user_id))
            
            db.commit()
            cursor.close()
            db.close()
            
            # Send verification email
            try:
                success, message = email_service.send_verification_email(email, user_name, verification_token)
                
                if success:
                    self.log_email_attempt(user_id, email, 'verification', 
                                         'Verify your SkillSwap account', 'sent')
                    log_user_action(user_id, "verification_email_resent", {
                        "email": email,
                        "ip_address": ip_address
                    })
                    return True, "Verification email sent! Please check your inbox."
                else:
                    self.log_email_attempt(user_id, email, 'verification', 
                                         'Verify your SkillSwap account', 'failed', message)
                    raise EmailException("Failed to send verification email")
                    
            except Exception as e:
                self.log_email_attempt(user_id, email, 'verification', 
                                     'Verify your SkillSwap account', 'failed', str(e))
                raise EmailException("Failed to send verification email")
            
        except mysql.connector.Error as e:
            raise DatabaseException("Failed to resend verification email", original_error=e)
