-- Add email verification and password reset functionality to the database

-- Add email verification fields to users table
ALTER TABLE users 
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN email_verification_token VARCHAR(255) NULL,
ADD COLUMN email_verification_expires TIMESTAMP NULL,
ADD COLUMN password_reset_token VARCHAR(255) NULL,
ADD COLUMN password_reset_expires TIMESTAMP NULL,
ADD COLUMN login_attempts INT DEFAULT 0,
ADD COLUMN account_locked_until TIMESTAMP NULL;

-- Create email verification tokens table for better tracking
CREATE TABLE email_verification_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires (expires_at)
);

-- Create password reset tokens table for better tracking
CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL,
    is_used BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires (expires_at)
);

-- Create email logs table for tracking sent emails
CREATE TABLE email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    email_address VARCHAR(255) NOT NULL,
    email_type ENUM('verification', 'password_reset', 'welcome', 'notification') NOT NULL,
    subject VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sent', 'failed', 'bounced') DEFAULT 'sent',
    error_message TEXT NULL,
    template_used VARCHAR(100) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_email (email_address),
    INDEX idx_type (email_type),
    INDEX idx_sent_at (sent_at)
);

-- Update users table constraints to make login more secure
ALTER TABLE users 
ADD CONSTRAINT chk_login_attempts CHECK (login_attempts >= 0 AND login_attempts <= 10);
