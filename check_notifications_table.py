import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'ShreeKrishna@7'),
    'database': os.getenv('DB_NAME', 'skill_swap')
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("Connected to database successfully!")
    
    # Check if notifications table exists
    cursor.execute("SHOW TABLES LIKE 'notifications'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Notifications table exists")
        
        # Check table structure
        cursor.execute("DESCRIBE notifications")
        columns = cursor.fetchall()
        print("\nNotifications table structure:")
        for column in columns:
            print(f"  {column[0]} - {column[1]}")
            
        # Check if there are any users
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        user_count = cursor.fetchone()[0]
        print(f"\n✅ Active users count: {user_count}")
        
        if user_count == 0:
            print("⚠️  No active users found - notifications won't be sent")
        
    else:
        print("❌ Notifications table does not exist")
        print("Creating notifications table...")
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                type ENUM('skill_swap_request', 'request_accepted', 'request_declined', 'message') DEFAULT 'skill_swap_request',
                title VARCHAR(255) NOT NULL,
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                related_request_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("✅ Notifications table created successfully!")
        
except mysql.connector.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
