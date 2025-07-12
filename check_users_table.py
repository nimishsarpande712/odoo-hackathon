import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'ShreeKrishna@7'),
    'database': os.getenv('DB_NAME', 'skill_swap')
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check users table structure
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    print("Users table structure:")
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
        
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\nTotal users: {user_count}")
    
    # Check for banned users (if name contains BANNED)
    cursor.execute("SELECT COUNT(*) FROM users WHERE name NOT LIKE '%BANNED%'")
    active_users = cursor.fetchone()[0]
    print(f"Active users (not banned): {active_users}")
        
except mysql.connector.Error as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
