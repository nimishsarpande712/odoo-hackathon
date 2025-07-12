#!/usr/bin/env python3
"""
Test script to verify availability functionality
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_availability_flow():
    """Test the complete availability flow"""
    session = requests.Session()
    
    print("=== Testing Availability Flow ===")
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_data = {
        'username': 'chetan',  # Use existing user
        'password': 'Test123!'  # You'll need to use the actual password
    }
    
    login_response = session.post(f'{BASE_URL}/login', json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.json()}")
    
    if login_response.status_code != 200:
        print("❌ Login failed! Cannot test availability.")
        return
    
    # Step 2: Check session
    print("\n2. Checking session...")
    session_response = session.get(f'{BASE_URL}/session-test')
    print(f"Session Status: {session_response.status_code}")
    print(f"Session Data: {session_response.json()}")
    
    # Step 3: Add availability
    print("\n3. Adding availability...")
    availability_data = {
        'day': 'Monday',
        'time_slot': 'Evening'
    }
    
    availability_response = session.post(f'{BASE_URL}/availability', json=availability_data)
    print(f"Availability Status: {availability_response.status_code}")
    print(f"Availability Response: {availability_response.json()}")
    
    if availability_response.status_code == 201:
        print("✅ Availability added successfully!")
    else:
        print("❌ Failed to add availability")

if __name__ == '__main__':
    test_availability_flow()
