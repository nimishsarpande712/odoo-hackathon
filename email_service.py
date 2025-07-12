import smtplib
import ssl
import secrets
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Tuple, Optional
import logging
import os
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailConfig:
    """Email configuration settings"""
    
    # SMTP Configuration - Use environment variables for security
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-app-password')  # Use app password for Gmail
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@skillswap.com')
    FROM_NAME = os.getenv('FROM_NAME', 'SkillSwap Platform')
    
    # Application settings
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
    TOKEN_EXPIRY_HOURS = int(os.getenv('TOKEN_EXPIRY_HOURS', 24))
    PASSWORD_RESET_EXPIRY_HOURS = int(os.getenv('PASSWORD_RESET_EXPIRY_HOURS', 1))
    
    # Security settings
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_MINUTES', 30))

class EmailService:
    """Email service for sending verification and password reset emails"""
    
    def __init__(self):
        self.config = EmailConfig()
        
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        token = secrets.token_urlsafe(length)
        # Add timestamp hash for uniqueness
        timestamp = str(datetime.utcnow().timestamp())
        hash_suffix = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        return f"{token}{hash_suffix}"
    
    def create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls(context=ssl.create_default_context())
            server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            raise Exception(f"Email service unavailable: {str(e)}")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> Tuple[bool, str]:
        """Send an email with both HTML and text versions"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            message["To"] = to_email
            
            # Add text version if provided
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email
            with self.create_smtp_connection() as server:
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_verification_email_template(self, user_name: str, verification_link: str) -> Tuple[str, str]:
        """Get email verification email template"""
        subject = "Verify your SkillSwap account"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
                .content { padding: 40px 30px; }
                .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
                .button:hover { opacity: 0.9; }
                .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to SkillSwap!</h1>
                    <p>Verify your email to get started</p>
                </div>
                <div class="content">
                    <h2>Hello {{ user_name }}!</h2>
                    <p>Thank you for joining SkillSwap, the platform where skills meet opportunity!</p>
                    <p>To complete your registration and start connecting with other skill enthusiasts, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{{ verification_link }}" class="button">Verify My Email</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace;">{{ verification_link }}</p>
                    
                    <div class="warning">
                        <strong>Security Notice:</strong> This verification link will expire in 24 hours. If you didn't create an account with SkillSwap, please ignore this email.
                    </div>
                    
                    <p>Once verified, you'll be able to:</p>
                    <ul>
                        <li>Browse and connect with other skill sharers</li>
                        <li>Offer your skills to help others learn</li>
                        <li>Request to learn new skills from experts</li>
                        <li>Build your professional network</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>© {{ current_year }} SkillSwap Platform. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply to this address.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        text_template = Template("""
        Welcome to SkillSwap!
        
        Hello {{ user_name }}!
        
        Thank you for joining SkillSwap. To complete your registration, please verify your email address by visiting this link:
        
        {{ verification_link }}
        
        This verification link will expire in 24 hours.
        
        If you didn't create an account with SkillSwap, please ignore this email.
        
        Best regards,
        The SkillSwap Team
        """)
        
        html_body = html_template.render(
            user_name=user_name,
            verification_link=verification_link,
            current_year=datetime.now().year
        )
        
        text_body = text_template.render(
            user_name=user_name,
            verification_link=verification_link
        )
        
        return subject, html_body, text_body
    
    def get_password_reset_email_template(self, user_name: str, reset_link: str) -> Tuple[str, str]:
        """Get password reset email template"""
        subject = "Reset your SkillSwap password"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                .header { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 30px; text-align: center; }
                .content { padding: 40px 30px; }
                .button { display: inline-block; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
                .button:hover { opacity: 0.9; }
                .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }
                .warning { background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; color: #721c24; }
                .security-tips { background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; color: #0c5460; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                    <p>Secure your SkillSwap account</p>
                </div>
                <div class="content">
                    <h2>Hello {{ user_name }}!</h2>
                    <p>We received a request to reset the password for your SkillSwap account.</p>
                    <p>If you requested this password reset, click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{{ reset_link }}" class="button">Reset My Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace;">{{ reset_link }}</p>
                    
                    <div class="warning">
                        <strong>Important Security Information:</strong>
                        <ul>
                            <li>This password reset link will expire in 1 hour for security</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Your current password remains unchanged until you complete the reset</li>
                        </ul>
                    </div>
                    
                    <div class="security-tips">
                        <strong>Password Security Tips:</strong>
                        <ul>
                            <li>Use at least 8 characters with a mix of letters, numbers, and symbols</li>
                            <li>Don't reuse passwords from other accounts</li>
                            <li>Consider using a password manager</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>© {{ current_year }} SkillSwap Platform. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply to this address.</p>
                    <p>If you're having trouble, contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        text_template = Template("""
        Password Reset Request
        
        Hello {{ user_name }}!
        
        We received a request to reset the password for your SkillSwap account.
        
        If you requested this password reset, visit this link to create a new password:
        
        {{ reset_link }}
        
        IMPORTANT SECURITY INFORMATION:
        - This password reset link will expire in 1 hour
        - If you didn't request this reset, please ignore this email
        - Your current password remains unchanged until you complete the reset
        
        Password Security Tips:
        - Use at least 8 characters with a mix of letters, numbers, and symbols
        - Don't reuse passwords from other accounts
        - Consider using a password manager
        
        Best regards,
        The SkillSwap Team
        """)
        
        html_body = html_template.render(
            user_name=user_name,
            reset_link=reset_link,
            current_year=datetime.now().year
        )
        
        text_body = text_template.render(
            user_name=user_name,
            reset_link=reset_link
        )
        
        return subject, html_body, text_body
    
    def send_verification_email(self, user_email: str, user_name: str, verification_token: str) -> Tuple[bool, str]:
        """Send email verification email"""
        try:
            verification_link = f"{self.config.BASE_URL}/verify-email?token={verification_token}"
            subject, html_body, text_body = self.get_verification_email_template(user_name, verification_link)
            return self.send_email(user_email, subject, html_body, text_body)
        except Exception as e:
            return False, f"Failed to send verification email: {str(e)}"
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> Tuple[bool, str]:
        """Send password reset email"""
        try:
            reset_link = f"{self.config.BASE_URL}/reset-password?token={reset_token}"
            subject, html_body, text_body = self.get_password_reset_email_template(user_name, reset_link)
            return self.send_email(user_email, subject, html_body, text_body)
        except Exception as e:
            return False, f"Failed to send password reset email: {str(e)}"

# Initialize email service
email_service = EmailService()
