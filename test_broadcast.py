import requests
import json

# Test admin login and broadcast message functionality

# Admin login
login_data = {
    "username": "admin",
    "password": "admin123"
}

session = requests.Session()

try:
    # Test admin login
    print("Testing admin login...")
    login_response = session.post("http://localhost:5000/admin/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.json()}")
    
    if login_response.status_code == 200:
        # Test broadcast message
        print("\nTesting broadcast message...")
        message_data = {
            "title": "Test Broadcast",
            "message": "This is a test broadcast message from admin!"
        }
        
        message_response = session.post("http://localhost:5000/admin/send_message", json=message_data)
        print(f"Message Status: {message_response.status_code}")
        print(f"Message Response: {message_response.json()}")
        
        # Test fetching notifications (would need a user session)
        print("\nBroadcast message functionality test completed!")
    else:
        print("Admin login failed!")
        
except Exception as e:
    print(f"Error testing functionality: {e}")
