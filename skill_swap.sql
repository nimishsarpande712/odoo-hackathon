CREATE DATABASE IF NOT EXISTS skill_swap;
USE skill_swap;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL CHECK (CHAR_LENGTH(name) >= 2 AND name REGEXP '^[a-zA-Z\\s\\-\']+$'),
    email VARCHAR(255) UNIQUE NOT NULL CHECK (email REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'),
    password_hash VARCHAR(255) NOT NULL,
    location VARCHAR(255) CHECK (location IS NULL OR (CHAR_LENGTH(location) >= 2 AND location REGEXP '^[a-zA-Z0-9\\s,.\\-()]+$')),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL CHECK (CHAR_LENGTH(name) >= 2 AND name REGEXP '^[a-zA-Z0-9\\s\\-\\.+#]+$'),
    category VARCHAR(100) CHECK (category IS NULL OR CHAR_LENGTH(category) <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE user_skills_offered (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill_offered (user_id, skill_id)
);


CREATE TABLE user_skills_wanted (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    desired_level ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'intermediate',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill_wanted (user_id, skill_id)
);


CREATE TABLE availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    day VARCHAR(20) CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    time_slot VARCHAR(50) CHECK (time_slot IN ('Morning', 'Afternoon', 'Evening', 'Night')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Skill Swap Requests Table
CREATE TABLE skill_swap_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requester_id INT NOT NULL,
    requestee_id INT NOT NULL,
    message TEXT,
    status ENUM('pending', 'accepted', 'declined', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (requestee_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_request (requester_id, requestee_id)
);

-- Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('skill_swap_request', 'request_accepted', 'request_declined', 'message') DEFAULT 'skill_swap_request',
    title VARCHAR(255) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    related_request_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (related_request_id) REFERENCES skill_swap_requests(id) ON DELETE CASCADE
);
