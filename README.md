# SkillSwap Platform - Enhanced with Email Verification & Password Reset

A comprehensive skill-sharing platform where users can connect, learn, and teach skills to each other. Now featuring secure email verification and password reset functionality.

## 🚀 New Features Added

### 🔐 Enhanced Security & Authentication
- **Email Verification**: Users must verify their email before accessing the platform
- **Password Reset**: Secure password reset via email with time-limited tokens
- **Account Security**: Protection against brute force attacks with account lockout
- **Rate Limiting**: Protection against spam and abuse
- **Enhanced Error Handling**: Comprehensive error tracking and user-friendly messages

### 📧 Email System
- **SMTP Integration**: Professional email delivery using SMTP
- **Beautiful Email Templates**: HTML and text email templates
- **Email Logging**: Track all email communications
- **Multiple Email Types**: Verification, password reset, notifications

### 🛡️ Security Improvements
- **Secure Token Generation**: Cryptographically secure tokens
- **Token Expiration**: Time-limited tokens for security
- **Login Attempt Tracking**: Monitor and prevent suspicious activity
- **Input Validation**: Enhanced validation for all user inputs

## 📋 Prerequisites

- Python 3.7+
- Node.js 14+
- MySQL 5.7+
- SMTP Email Account (Gmail recommended)

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd "c:\Projects\skill swap odoo\odoo-hackathon"
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```
   
   This script will:
   - Install Python dependencies
   - Guide you through configuration
   - Create the `.env` file
   - Test database connection
   - Apply schema updates
   - Test email configuration

### Option 2: Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Apply database schema**:
   ```bash
   mysql -u root -p skill_swap < email_verification_schema.sql
   ```

4. **Start the backend**:
   ```bash
   python app.py
   ```

5. **Start the frontend**:
   ```bash
   cd ../skill-swap
   npm install
   npm start
   ```

## ⚙️ Configuration

### Database Configuration
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=skill_swap
```

### Email Configuration (Gmail Example)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
FROM_EMAIL=noreply@skillswap.com
FROM_NAME=SkillSwap Platform
```

### Security Configuration
```env
SECRET_KEY=your-secret-key-change-in-production
TOKEN_EXPIRY_HOURS=24
PASSWORD_RESET_EXPIRY_HOURS=1
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30
```

## 📧 Email Setup Instructions

### For Gmail:

1. **Enable 2-Factor Authentication**:
   - Go to Google Account settings
   - Enable 2-factor authentication

2. **Generate App Password**:
   - Visit: https://support.google.com/accounts/answer/185833
   - Generate an app password
   - Use this password in `SMTP_PASSWORD`

3. **Configure .env**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   ```

### For Other Email Providers:

**Outlook/Hotmail**:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo**:
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## 🚪 New Authentication Flow

### User Registration:
1. User fills registration form
2. Account created (unverified)
3. Verification email sent
4. User clicks verification link
5. Account activated
6. User can now log in

### Password Reset:
1. User clicks "Forgot Password"
2. Enters email address
3. Reset email sent (if account exists)
4. User clicks reset link
5. Sets new password
6. Account unlocked and ready for login

### Login Security:
- Email verification required
- Account lockout after failed attempts
- Rate limiting on login attempts
- Secure session management

## 🎯 New API Endpoints

### Authentication Endpoints:
- `POST /register` - Register with email verification
- `POST /login` - Login with verification check
- `POST /verify-email` - Verify email address
- `POST /resend-verification` - Resend verification email
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token
- `GET /check-auth` - Check authentication status
- `POST /logout` - Secure logout

### Enhanced Features:
- Comprehensive error handling
- Rate limiting protection
- Security logging
- Email delivery tracking

## 🎨 New Frontend Components

### Email Verification:
- `EmailVerification.jsx` - Email verification page
- Automatic redirect after verification
- Resend verification option
- Error handling and user guidance

### Password Reset:
- `ForgotPassword.jsx` - Request password reset
- `ResetPassword.jsx` - Set new password
- Password strength indicator
- Security notifications

### Enhanced Login/Register:
- Updated with verification flow
- Better error messages
- "Forgot Password" integration
- Email verification prompts

## 🔒 Security Features

### Password Security:
- Minimum 8 characters
- Mixed case requirements
- Number requirements
- bcrypt hashing with salt

### Token Security:
- Cryptographically secure generation
- Time-limited expiration
- Single-use tokens
- Secure storage and validation

### Account Protection:
- Login attempt limiting
- Account lockout mechanism
- IP-based rate limiting
- Suspicious activity logging

## 📊 Database Schema Updates

### New Tables:
- `email_verification_tokens` - Track verification tokens
- `password_reset_tokens` - Track reset tokens
- `email_logs` - Log all email communications

### Updated Users Table:
- `email_verified` - Verification status
- `login_attempts` - Failed login counter
- `account_locked_until` - Lockout timestamp
- Token fields for compatibility

## 🧪 Testing

### Test Email Configuration:
```bash
python -c "
from email_service import email_service
success, msg = email_service.send_email(
    'your-email@example.com',
    'Test Email',
    '<h1>Test</h1><p>Email working!</p>',
    'Test Email - Email working!'
)
print(f'Success: {success}, Message: {msg}')
"
```

### Test Database Connection:
```bash
python -c "
from auth_service import AuthService
from app import DB_CONFIG
auth = AuthService(DB_CONFIG)
conn = auth.get_db_connection()
print('Database connection successful!')
conn.close()
"
```

## 🚨 Troubleshooting

### Common Issues:

**Email Not Sending**:
- Check SMTP credentials
- Verify app password (Gmail)
- Check firewall settings
- Test with setup script

**Database Connection Failed**:
- Verify MySQL is running
- Check credentials in .env
- Ensure database exists
- Check MySQL user permissions

**Email Verification Not Working**:
- Check email in spam folder
- Verify base URL in .env
- Check token expiration
- Test email configuration

**Password Reset Issues**:
- Ensure email is verified first
- Check token expiration time
- Verify SMTP settings
- Check rate limiting

### Debug Mode:
Enable detailed logging by setting:
```env
FLASK_ENV=development
```

## 📚 Documentation

### Email Templates:
- Located in `email_service.py`
- Customizable HTML and text versions
- Responsive design
- Professional styling

### Error Handling:
- Centralized in `error_handling.py`
- Standardized error codes
- User-friendly messages
- Comprehensive logging

### Validation:
- Enhanced in `validators.py`
- Real-time validation
- Security-focused checks
- User guidance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure email functionality works
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check this README
2. Run the setup script for diagnostics
3. Check the troubleshooting section
4. Review error logs
5. Contact support team

## 🎉 Success!

Your SkillSwap platform now includes:
- ✅ Secure email verification
- ✅ Password reset functionality  
- ✅ Enhanced security measures
- ✅ Professional email templates
- ✅ Comprehensive error handling
- ✅ Rate limiting and protection
- ✅ Beautiful user interface
- ✅ Database logging and tracking

Start connecting, learning, and sharing skills securely! 🚀
