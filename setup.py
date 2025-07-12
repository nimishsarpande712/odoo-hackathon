#!/usr/bin/env python3
"""
SkillSwap Setup Script
This script helps set up the SkillSwap application with email verification and password reset features.
"""

import os
import sys
import subprocess
import mysql.connector
from getpass import getpass

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    print("✅ Python version check passed")

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        overwrite = input("📝 .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("⏭️  Skipping .env file creation")
            return
    
    print("📝 Creating .env file...")
    
    # Database configuration
    print("\n🗄️  Database Configuration:")
    db_host = input("Database host (localhost): ") or "localhost"
    db_user = input("Database user (root): ") or "root"
    db_password = getpass("Database password: ")
    db_name = input("Database name (skill_swap): ") or "skill_swap"
    
    # Email configuration
    print("\n📧 Email Configuration:")
    print("For Gmail, you'll need to:")
    print("1. Enable 2-factor authentication")
    print("2. Generate an App Password")
    print("3. Use the app password below")
    
    smtp_server = input("SMTP server (smtp.gmail.com): ") or "smtp.gmail.com"
    smtp_port = input("SMTP port (587): ") or "587"
    smtp_username = input("SMTP username (your email): ")
    smtp_password = getpass("SMTP password (app password): ")
    from_email = input("From email (noreply@skillswap.com): ") or "noreply@skillswap.com"
    from_name = input("From name (SkillSwap Platform): ") or "SkillSwap Platform"
    
    # Application configuration
    print("\n⚙️  Application Configuration:")
    secret_key = input("Secret key (press Enter to generate): ")
    if not secret_key:
        import secrets
        secret_key = secrets.token_hex(32)
        print(f"Generated secret key: {secret_key}")
    
    base_url = input("Base URL (http://localhost:3000): ") or "http://localhost:3000"
    
    # Write .env file
    env_content = f"""# SkillSwap Configuration
# Database Configuration
DB_HOST={db_host}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME={db_name}

# Email Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_USERNAME={smtp_username}
SMTP_PASSWORD={smtp_password}
FROM_EMAIL={from_email}
FROM_NAME={from_name}

# Application Configuration
SECRET_KEY={secret_key}
BASE_URL={base_url}
FLASK_ENV=development

# Security Settings
TOKEN_EXPIRY_HOURS=24
PASSWORD_RESET_EXPIRY_HOURS=1
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")

def test_database_connection():
    """Test database connection"""
    print("\n🔗 Testing database connection...")
    
    # Load environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    try:
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'skill_swap')
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def apply_schema_updates():
    """Apply database schema updates"""
    print("\n📊 Applying database schema updates...")
    
    if not os.path.exists('email_verification_schema.sql'):
        print("❌ Schema file not found")
        return False
    
    try:
        # Load environment variables
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()
        
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'skill_swap')
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Read and execute schema file
        with open('email_verification_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as e:
                    if "Duplicate column name" in str(e) or "already exists" in str(e):
                        print(f"⚠️  Column/table already exists, skipping: {e}")
                    else:
                        raise e
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Schema updates applied successfully")
        return True
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n📧 Testing email configuration...")
    
    test_email = input("Enter your email to test (or press Enter to skip): ")
    if not test_email:
        print("⏭️  Skipping email test")
        return True
    
    try:
        # Load environment variables
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()
        
        from email_service import email_service
        
        success, message = email_service.send_email(
            test_email,
            "SkillSwap Setup Test",
            "<h1>Test Email</h1><p>If you received this email, your email configuration is working correctly!</p>",
            "Test Email\n\nIf you received this email, your email configuration is working correctly!"
        )
        
        if success:
            print("✅ Email test successful! Check your inbox.")
            return True
        else:
            print(f"❌ Email test failed: {message}")
            return False
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 SkillSwap Setup Script")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Please fix database connection issues before continuing")
        sys.exit(1)
    
    # Apply schema updates
    if not apply_schema_updates():
        print("\n❌ Please fix schema issues before continuing")
        sys.exit(1)
    
    # Test email configuration
    email_works = test_email_configuration()
    
    # Final summary
    print("\n🎉 Setup Summary:")
    print("✅ Python requirements installed")
    print("✅ .env file created")
    print("✅ Database connection working")
    print("✅ Schema updates applied")
    
    if email_works:
        print("✅ Email configuration working")
    else:
        print("⚠️  Email configuration needs attention")
    
    print("\n📋 Next Steps:")
    print("1. Start the Flask backend: python app.py")
    print("2. Start the React frontend: npm start (in skill-swap directory)")
    print("3. Navigate to http://localhost:3000")
    
    if not email_works:
        print("\n⚠️  Email Issues:")
        print("- Check your SMTP credentials in .env")
        print("- For Gmail, ensure you're using an App Password")
        print("- Check your firewall/antivirus settings")

if __name__ == "__main__":
    main()
