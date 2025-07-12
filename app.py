from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv
from validators import validate_user_data, UserValidator
from auth_service import AuthService
from error_handling import (
    handle_errors, validate_request_data, log_user_action,
    SkillSwapException, ValidationException, AuthenticationException
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to support credentials (sessions/cookies)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_change_in_production')

# Database configuration
DB_CONFIG = {
    "host": os.getenv('DB_HOST', "localhost"),
    "user": os.getenv('DB_USER', "root"),
    "password": os.getenv('DB_PASSWORD', "ShreeKrishna@7"),
    "database": os.getenv('DB_NAME', "skill_swap")
}

# Initialize auth service
auth_service = AuthService(DB_CONFIG)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/register', methods=['POST'])
@handle_errors(include_details=True)
def register():
    """Register a new user with email verification"""
    data = validate_request_data(
        required_fields=['username', 'email', 'password'],
        optional_fields=['location', 'is_public']
    )
    
    # Map frontend field names to backend
    user_data = {
        'name': data.get('username'),
        'email': data.get('email').lower(),
        'password': data.get('password'),
        'location': data.get('location'),
        'is_public': data.get('is_public', True)
    }
    
    ip_address = request.remote_addr
    
    success, message, user_id = auth_service.register_user(user_data, ip_address)
    
    if success:
        log_user_action(user_id, "registration_completed", {
            "email": user_data['email'],
            "ip_address": ip_address
        })
        return jsonify({
            'success': True,
            'message': message,
            'user_id': user_id,
            'requires_verification': True
        }), 201
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/login', methods=['POST'])
@handle_errors(include_details=True)
def login():
    """Login user with enhanced security and email verification check"""
    data = validate_request_data(
        required_fields=['username', 'password']
    )
    
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    
    user_data, message = auth_service.login_user(username, password, ip_address)
    
    # Set session data
    session['username'] = user_data['name']
    session['user_id'] = user_data['user_id']
    session['email_verified'] = user_data['email_verified']
    
    return jsonify({
        'success': True,
        'message': message,
        'user_id': user_data['user_id'],
        'name': user_data['name'],
        'email_verified': user_data['email_verified']
    }), 200

@app.route('/skills', methods=['GET'])
def get_skills():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, category FROM skills ORDER BY name")
        skills = []
        for skill in cursor.fetchall():
            skills.append({
                'id': skill[0],
                'name': skill[1],
                'category': skill[2]
            })
        cursor.close()
        db.close()
        return jsonify({'skills': skills}), 200
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/add-skill', methods=['POST'])
def add_skill():
    data = request.get_json()
    name = data.get('name', '').strip()
    category = data.get('category', 'General').strip()
    
    # Validate skill name
    is_valid, message = UserValidator.validate_skill_name(name)
    if not is_valid:
        return jsonify({'message': message}), 400
    
    # Validate category
    if category and len(category) > 100:
        return jsonify({'message': 'Category must not exceed 100 characters'}), 400
        
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO skills (name, category) VALUES (%s, %s)", (name, category))
        db.commit()
        skill_id = cursor.lastrowid
        cursor.close()
        db.close()
        return jsonify({'message': 'Skill added successfully', 'skill_id': skill_id}), 201
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/user-skills-offered', methods=['POST'])
def add_offered_skill():
    data = request.get_json()
    user_id = session.get('user_id')
    skill_id = data.get('skill_id')
    proficiency_level = data.get('proficiency_level', 'beginner')
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    if not skill_id:
        return jsonify({'message': 'Skill ID is required'}), 400
    
    # Validate proficiency level
    is_valid, message = UserValidator.validate_proficiency_level(proficiency_level)
    if not is_valid:
        return jsonify({'message': message}), 400
        
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if skill exists
        cursor.execute("SELECT id FROM skills WHERE id = %s", (skill_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'message': 'Invalid skill ID'}), 400
        
        # Insert offered skill
        cursor.execute("INSERT INTO user_skills_offered (user_id, skill_id, proficiency_level) VALUES (%s, %s, %s)", 
                      (user_id, skill_id, proficiency_level))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'message': 'Offered skill added successfully'}), 201
        
    except mysql.connector.IntegrityError as err:
        if "Duplicate entry" in str(err):
            return jsonify({'message': 'You have already offered this skill'}), 409
        return jsonify({'message': f'Database error: {err}'}), 500
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/user-skills-wanted', methods=['POST'])
def add_wanted_skill():
    data = request.get_json()
    user_id = session.get('user_id')
    skill_id = data.get('skill_id')
    desired_level = data.get('desired_level', 'intermediate')
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    if not skill_id:
        return jsonify({'message': 'Skill ID is required'}), 400
    
    # Validate desired level
    is_valid, message = UserValidator.validate_proficiency_level(desired_level)
    if not is_valid:
        return jsonify({'message': message}), 400
        
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if skill exists
        cursor.execute("SELECT id FROM skills WHERE id = %s", (skill_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
        
        # Insert wanted skill
        cursor.execute("INSERT INTO user_skills_wanted (user_id, skill_id, desired_level) VALUES (%s, %s, %s)", 
                      (user_id, skill_id, desired_level))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'message': 'Wanted skill added successfully'}), 201
        
    except mysql.connector.IntegrityError as err:
        if "Duplicate entry" in str(err):
            return jsonify({'message': 'You have already added this skill to wanted list'}), 409
        return jsonify({'message': f'Database error: {err}'}), 500
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/availability', methods=['POST'])
def add_availability():
    data = request.get_json()
    user_id = session.get('user_id')
    day = data.get('day', '').strip()
    time_slot = data.get('time_slot', '').strip()
    
    print(f"DEBUG: Session data: {dict(session)}")  # Debug session
    print(f"DEBUG: User ID from session: {user_id}")  # Debug user_id
    print(f"DEBUG: Received data: {data}")  # Debug received data
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    # Validate day
    is_valid, message = UserValidator.validate_day(day)
    if not is_valid:
        return jsonify({'message': message}), 400
    
    # Validate time slot
    is_valid, message = UserValidator.validate_time_slot(time_slot)
    if not is_valid:
        return jsonify({'message': message}), 400
        
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO availability (user_id, day, time_slot) VALUES (%s, %s, %s)", 
                      (user_id, day, time_slot))
        db.commit()
        cursor.close()
        db.close()
        print(f"DEBUG: Successfully inserted availability for user {user_id}")  # Debug success
        return jsonify({'message': 'Availability added successfully'}), 201
    except mysql.connector.Error as err:
        print(f"DEBUG: Database error: {err}")  # Debug database error
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/logout', methods=['POST'])
@handle_errors()
def logout():
    """Logout user"""
    user_id = session.get('user_id')
    if user_id:
        log_user_action(user_id, "logout", {"ip_address": request.remote_addr})
    
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

@app.route('/validate-email', methods=['POST'])
def validate_email():
    """Endpoint to validate email in real-time"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    # Validate email format
    is_valid, message = UserValidator.validate_email(email)
    if not is_valid:
        return jsonify({'valid': False, 'message': message}), 200
    
    # Check if email already exists
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'valid': False, 'message': 'Email already registered'}), 200
        
        cursor.close()
        db.close()
        return jsonify({'valid': True, 'message': 'Email is available'}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'valid': False, 'message': 'Unable to validate email'}), 500

@app.route('/validate-username', methods=['POST'])
def validate_username():
    """Endpoint to validate username in real-time"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    # Validate username format
    is_valid, message = UserValidator.validate_name(username)
    if not is_valid:
        return jsonify({'valid': False, 'message': message}), 200
    
    # Check if username already exists
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'valid': False, 'message': 'Username already taken'}), 200
        
        cursor.close()
        db.close()
        return jsonify({'valid': True, 'message': 'Username is available'}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'valid': False, 'message': 'Unable to validate username'}), 500

@app.route('/session-test', methods=['GET'])
def session_test():
    """Test endpoint to check session status"""
    return jsonify({
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'has_session': bool(session)
    }), 200

@app.route('/profiles', methods=['GET'])
def get_all_profiles():
    """Get all user profiles with their skills and availability for dashboard (excludes current user)"""
    current_user_id = session.get('user_id')
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Get all public users with their details, excluding current user
        if current_user_id:
            cursor.execute("""
                SELECT u.id, u.name, u.email, u.location, u.is_public, u.created_at
                FROM users u 
                WHERE u.is_public = TRUE AND u.id != %s
                ORDER BY u.created_at DESC
            """, (current_user_id,))
        else:
            # If no user is logged in, show all public profiles
            cursor.execute("""
                SELECT u.id, u.name, u.email, u.location, u.is_public, u.created_at
                FROM users u 
                WHERE u.is_public = TRUE
                ORDER BY u.created_at DESC
            """)
        
        users = []
        for user_row in cursor.fetchall():
            user_id, name, email, location, is_public, created_at = user_row
            
            # Get offered skills for this user
            cursor.execute("""
                SELECT s.name, uso.proficiency_level
                FROM user_skills_offered uso
                JOIN skills s ON uso.skill_id = s.id
                WHERE uso.user_id = %s
            """, (user_id,))
            offered_skills = [{'name': skill[0], 'proficiency': skill[1]} for skill in cursor.fetchall()]
            
            # Get wanted skills for this user
            cursor.execute("""
                SELECT s.name, usw.desired_level
                FROM user_skills_wanted usw
                JOIN skills s ON usw.skill_id = s.id
                WHERE usw.user_id = %s
            """, (user_id,))
            wanted_skills = [{'name': skill[0], 'desired_level': skill[1]} for skill in cursor.fetchall()]
            
            # Get availability for this user
            cursor.execute("""
                SELECT day, time_slot
                FROM availability
                WHERE user_id = %s
            """, (user_id,))
            availability = [{'day': av[0], 'time_slot': av[1]} for av in cursor.fetchall()]
            
            # Only include users who have completed their profile (have at least one skill)
            if offered_skills or wanted_skills:
                users.append({
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'location': location,
                    'offered_skills': offered_skills,
                    'wanted_skills': wanted_skills,
                    'availability': availability,
                    'created_at': created_at.isoformat() if created_at else None
                })
        
        cursor.close()
        db.close()
        return jsonify({'profiles': users}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/profile/current', methods=['GET'])
def get_current_user_profile():
    """Get current user's profile data"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Get user details
        cursor.execute("""
            SELECT id, name, email, location, is_public, created_at
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user_row = cursor.fetchone()
        if not user_row:
            cursor.close()
            db.close()
            return jsonify({'message': 'User not found'}), 404
        
        user_id, name, email, location, is_public, created_at = user_row
        
        # Get offered skills
        cursor.execute("""
            SELECT s.id, s.name, uso.proficiency_level
            FROM user_skills_offered uso
            JOIN skills s ON uso.skill_id = s.id
            WHERE uso.user_id = %s
        """, (user_id,))
        offered_skills = [{'id': skill[0], 'name': skill[1], 'proficiency': skill[2]} for skill in cursor.fetchall()]
        
        # Get wanted skills
        cursor.execute("""
            SELECT s.id, s.name, usw.desired_level
            FROM user_skills_wanted usw
            JOIN skills s ON usw.skill_id = s.id
            WHERE usw.user_id = %s
        """, (user_id,))
        wanted_skills = [{'id': skill[0], 'name': skill[1], 'desired_level': skill[2]} for skill in cursor.fetchall()]
        
        # Get availability
        cursor.execute("""
            SELECT day, time_slot
            FROM availability
            WHERE user_id = %s
        """, (user_id,))
        availability = [{'day': av[0], 'time_slot': av[1]} for av in cursor.fetchall()]
        
        profile = {
            'id': user_id,
            'name': name,
            'email': email,
            'location': location,
            'is_public': is_public,
            'offered_skills': offered_skills,
            'wanted_skills': wanted_skills,
            'availability': availability,
            'created_at': created_at.isoformat() if created_at else None
        }
        
        cursor.close()
        db.close()
        return jsonify({'profile': profile}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/all-profiles', methods=['GET'])
def get_all_profiles_including_current():
    """Get ALL user profiles with their skills and availability (includes current user)"""
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Get all public users with their details (including current user)
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.location, u.is_public, u.created_at
            FROM users u 
            WHERE u.is_public = TRUE
            ORDER BY u.created_at DESC
        """)
        
        users = []
        current_user_id = session.get('user_id')
        
        for user_row in cursor.fetchall():
            user_id, name, email, location, is_public, created_at = user_row
            
            # Get offered skills for this user
            cursor.execute("""
                SELECT s.name, uso.proficiency_level
                FROM user_skills_offered uso
                JOIN skills s ON uso.skill_id = s.id
                WHERE uso.user_id = %s
            """, (user_id,))
            offered_skills = [{'name': skill[0], 'proficiency': skill[1]} for skill in cursor.fetchall()]
            
            # Get wanted skills for this user
            cursor.execute("""
                SELECT s.name, usw.desired_level
                FROM user_skills_wanted usw
                JOIN skills s ON usw.skill_id = s.id
                WHERE usw.user_id = %s
            """, (user_id,))
            wanted_skills = [{'name': skill[0], 'desired_level': skill[1]} for skill in cursor.fetchall()]
            
            # Get availability for this user
            cursor.execute("""
                SELECT day, time_slot
                FROM availability
                WHERE user_id = %s
            """, (user_id,))
            availability = [{'day': av[0], 'time_slot': av[1]} for av in cursor.fetchall()]
            
            # Include all users who have completed their profile (have at least one skill)
            if offered_skills or wanted_skills:
                users.append({
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'location': location,
                    'offered_skills': offered_skills,
                    'wanted_skills': wanted_skills,
                    'availability': availability,
                    'created_at': created_at.isoformat() if created_at else None,
                    'is_current_user': user_id == current_user_id  # Flag to identify current user
                })
        
        cursor.close()
        db.close()
        return jsonify({'profiles': users}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/skill-swap-request', methods=['POST'])
def send_skill_swap_request():
    """Send a skill swap request to another user"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    data = request.get_json()
    requestee_id = data.get('requestee_id')
    message = data.get('message', '').strip()
    
    if not requestee_id:
        return jsonify({'message': 'Requestee ID is required'}), 400
    
    if requestee_id == current_user_id:
        return jsonify({'message': 'Cannot send request to yourself'}), 400
    
    # Validate message length
    if len(message) > 500:
        return jsonify({'message': 'Message must not exceed 500 characters'}), 400
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if requestee exists and is public
        cursor.execute("SELECT id, name FROM users WHERE id = %s AND is_public = TRUE", (requestee_id,))
        requestee = cursor.fetchone()
        if not requestee:
            cursor.close()
            db.close()
            return jsonify({'message': 'User not found or not available for skill swap'}), 404
        
        # Get current user name
        cursor.execute("SELECT name FROM users WHERE id = %s", (current_user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            cursor.close()
            db.close()
            return jsonify({'message': 'Current user not found'}), 404
        
        # Insert skill swap request
        cursor.execute("""
            INSERT INTO skill_swap_requests (requester_id, requestee_id, message, status) 
            VALUES (%s, %s, %s, 'pending')
        """, (current_user_id, requestee_id, message))
        
        request_id = cursor.lastrowid
        
        # Create notification for the requestee
        notification_title = f"New Skill Swap Request from {current_user[0]}"
        notification_message = message if message else "Would like to connect for skill swapping"
        
        cursor.execute("""
            INSERT INTO notifications (user_id, type, title, message, related_request_id) 
            VALUES (%s, 'skill_swap_request', %s, %s, %s)
        """, (requestee_id, notification_title, notification_message, request_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'message': 'Skill swap request sent successfully',
            'request_id': request_id
        }), 201
        
    except mysql.connector.IntegrityError as err:
        if "Duplicate entry" in str(err):
            return jsonify({'message': 'You have already sent a request to this user'}), 409
        return jsonify({'message': f'Database error: {err}'}), 500
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/skill-swap-requests', methods=['GET'])
def get_skill_swap_requests():
    """Get skill swap requests (sent and received) for current user"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    request_type = request.args.get('type', 'all')  # 'sent', 'received', or 'all'
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        requests_data = {'sent': [], 'received': []}
        
        if request_type in ['sent', 'all']:
            # Get sent requests
            cursor.execute("""
                SELECT sr.id, sr.requestee_id, u.name, u.email, sr.message, sr.status, sr.created_at
                FROM skill_swap_requests sr
                JOIN users u ON sr.requestee_id = u.id
                WHERE sr.requester_id = %s
                ORDER BY sr.created_at DESC
            """, (current_user_id,))
            
            for req in cursor.fetchall():
                requests_data['sent'].append({
                    'id': req[0],
                    'user_id': req[1],
                    'user_name': req[2],
                    'user_email': req[3],
                    'message': req[4],
                    'status': req[5],
                    'created_at': req[6].isoformat() if req[6] else None
                })
        
        if request_type in ['received', 'all']:
            # Get received requests
            cursor.execute("""
                SELECT sr.id, sr.requester_id, u.name, u.email, sr.message, sr.status, sr.created_at
                FROM skill_swap_requests sr
                JOIN users u ON sr.requester_id = u.id
                WHERE sr.requestee_id = %s
                ORDER BY sr.created_at DESC
            """, (current_user_id,))
            
            for req in cursor.fetchall():
                requests_data['received'].append({
                    'id': req[0],
                    'user_id': req[1],
                    'user_name': req[2],
                    'user_email': req[3],
                    'message': req[4],
                    'status': req[5],
                    'created_at': req[6].isoformat() if req[6] else None
                })
        
        cursor.close()
        db.close()
        
        return jsonify({'requests': requests_data}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/skill-swap-request/<int:request_id>/respond', methods=['POST'])
def respond_to_skill_swap_request(request_id):
    """Accept or decline a skill swap request"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    data = request.get_json()
    response = data.get('response')  # 'accepted' or 'declined'
    
    if response not in ['accepted', 'declined']:
        return jsonify({'message': 'Invalid response. Must be "accepted" or "declined"'}), 400
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if request exists and is for current user
        cursor.execute("""
            SELECT sr.id, sr.requester_id, u.name, sr.status
            FROM skill_swap_requests sr
            JOIN users u ON sr.requester_id = u.id
            WHERE sr.id = %s AND sr.requestee_id = %s
        """, (request_id, current_user_id))
        
        request_data = cursor.fetchone()
        if not request_data:
            cursor.close()
            db.close()
            return jsonify({'message': 'Request not found or not authorized'}), 404
        
        req_id, requester_id, requester_name, current_status = request_data
        
        if current_status != 'pending':
            cursor.close()
            db.close()
            return jsonify({'message': 'Request has already been responded to'}), 400
        
        # Update request status
        cursor.execute("""
            UPDATE skill_swap_requests 
            SET status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (response, request_id))
        
        # Get current user name
        cursor.execute("SELECT name FROM users WHERE id = %s", (current_user_id,))
        current_user_name = cursor.fetchone()[0]
        
        # Create notification for the requester
        if response == 'accepted':
            notification_title = f"{current_user_name} accepted your skill swap request!"
            notification_message = f"Great news! {current_user_name} has accepted your skill swap request. You can now contact them to arrange your skill exchange."
        else:
            notification_title = f"{current_user_name} declined your skill swap request"
            notification_message = f"{current_user_name} has declined your skill swap request. Don't worry, there are many other opportunities!"
        
        cursor.execute("""
            INSERT INTO notifications (user_id, type, title, message, related_request_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (requester_id, f'request_{response}', notification_title, notification_message, request_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'message': f'Request {response} successfully',
            'status': response
        }), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for current user"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 20))
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        query = """
            SELECT id, type, title, message, is_read, related_request_id, created_at
            FROM notifications
            WHERE user_id = %s
        """
        params = [current_user_id]
        
        if unread_only:
            query += " AND is_read = FALSE"
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        
        notifications = []
        for notif in cursor.fetchall():
            notifications.append({
                'id': notif[0],
                'type': notif[1],
                'title': notif[2],
                'message': notif[3],
                'is_read': notif[4],
                'related_request_id': notif[5],
                'created_at': notif[6].isoformat() if notif[6] else None
            })
        
        # Get unread count
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", (current_user_id,))
        unread_count = cursor.fetchone()[0]
        
        cursor.close()
        db.close()
        
        return jsonify({
            'notifications': notifications,
            'unread_count': unread_count
        }), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE id = %s AND user_id = %s
        """, (notification_id, current_user_id))
        
        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return jsonify({'message': 'Notification not found'}), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

@app.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE user_id = %s AND is_read = FALSE
        """, (current_user_id,))
        
        updated_count = cursor.rowcount
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'message': f'Marked {updated_count} notifications as read'
        }), 200
        
    except mysql.connector.Error as err:
        return jsonify({'message': f'Database error: {err}'}), 500

# Email verification and password reset endpoints
@app.route('/verify-email', methods=['POST'])
@handle_errors(include_details=True)
def verify_email():
    """Verify user email address"""
    data = validate_request_data(required_fields=['token'])
    token = data.get('token')
    ip_address = request.remote_addr
    
    success, message = auth_service.verify_email(token, ip_address)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@app.route('/resend-verification', methods=['POST'])
@handle_errors(include_details=True)
def resend_verification():
    """Resend email verification"""
    data = validate_request_data(required_fields=['email'])
    email = data.get('email').lower()
    ip_address = request.remote_addr
    
    success, message = auth_service.resend_verification_email(email, ip_address)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200

@app.route('/forgot-password', methods=['POST'])
@handle_errors(include_details=True)
def forgot_password():
    """Request password reset"""
    data = validate_request_data(required_fields=['email'])
    email = data.get('email').lower()
    ip_address = request.remote_addr
    user_agent = str(request.user_agent)
    
    success, message = auth_service.request_password_reset(email, ip_address, user_agent)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200

@app.route('/reset-password', methods=['POST'])
@handle_errors(include_details=True)
def reset_password():
    """Reset password using token"""
    data = validate_request_data(required_fields=['token', 'password'])
    token = data.get('token')
    new_password = data.get('password')
    ip_address = request.remote_addr
    
    success, message = auth_service.reset_password(token, new_password, ip_address)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@app.route('/check-auth', methods=['GET'])
@handle_errors()
def check_auth():
    """Check if user is authenticated and email is verified"""
    user_id = session.get('user_id')
    username = session.get('username')
    email_verified = session.get('email_verified', False)
    
    if user_id and username:
        return jsonify({
            'authenticated': True,
            'user_id': user_id,
            'username': username,
            'email_verified': email_verified
        }), 200
    else:
        return jsonify({
            'authenticated': False,
            'email_verified': False
        }), 200

@app.route('/chat/<int:request_id>', methods=['GET'])
@handle_errors()
def get_chat_messages(request_id):
    """Get chat messages for a request"""
    if 'user_id' not in session:
        raise AuthenticationException("Please log in to access chat")
    
    user_id = session['user_id']
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user is part of this request
        cursor.execute("""
            SELECT requester_id, requestee_id 
            FROM skill_swap_requests 
            WHERE id = %s AND status = 'accepted'
        """, (request_id,))
        
        request_data = cursor.fetchone()
        if not request_data or user_id not in [request_data['requester_id'], request_data['requestee_id']]:
            return jsonify({'error': 'Unauthorized access to chat'}), 403
        
        # Get messages
        cursor.execute("""
            SELECT cm.id, cm.message, cm.sent_at, cm.sender_id,
                   cm.sender_id = %s as is_from_current_user
            FROM chat_messages cm
            WHERE cm.request_id = %s
            ORDER BY cm.sent_at ASC
        """, (user_id, request_id))
        
        messages = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'messages': messages
        })

@app.route('/chat/send', methods=['POST'])
@handle_errors()
def send_chat_message():
    """Send a chat message"""
    if 'user_id' not in session:
        raise AuthenticationException("Please log in to send messages")
    
    data = validate_request_data(
        required_fields=['request_id', 'message']
    )
    
    user_id = session['user_id']
    request_id = data['request_id']
    message = data['message'].strip()
    
    if not message:
        raise ValidationException("Message cannot be empty")
    
    if len(message) > 500:
        raise ValidationException("Message too long (max 500 characters)")
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user is part of this request
        cursor.execute("""
            SELECT requester_id, requestee_id 
            FROM skill_swap_requests 
            WHERE id = %s AND status = 'accepted'
        """, (request_id,))
        
        request_data = cursor.fetchone()
        if not request_data or user_id not in [request_data['requester_id'], request_data['requestee_id']]:
            return jsonify({'error': 'Unauthorized access to chat'}), 403
        
        # Insert message
        cursor.execute("""
            INSERT INTO chat_messages (request_id, sender_id, message, sent_at)
            VALUES (%s, %s, %s, NOW())
        """, (request_id, user_id, message))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })

# Admin routes
@app.route('/admin/login', methods=['POST'])
@handle_errors()
def admin_login():
    """Admin login endpoint"""
    data = validate_request_data(required_fields=['username', 'password'])
    username = data.get('username')
    password = data.get('password')
    
    # Simple admin credentials check (in production, use proper authentication)
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return jsonify({
            'success': True,
            'message': 'Admin login successful'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid admin credentials'
        }), 401

@app.route('/admin/skills', methods=['GET'])
@handle_errors()
def admin_get_skills():
    """Get all skills for admin panel"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, u.username, u.email 
            FROM skills s 
            JOIN users u ON s.user_id = u.id 
            ORDER BY s.created_at DESC
        """)
        skills = cursor.fetchall()
        
        for skill in skills:
            if skill['created_at']:
                skill['created_at'] = skill['created_at'].isoformat()
        
        return jsonify(skills)

@app.route('/admin/skills/<int:skill_id>', methods=['DELETE'])
@handle_errors()
def admin_reject_skill(skill_id):
    """Reject/delete a skill"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM skills WHERE id = %s", (skill_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Skill rejected successfully'})
        else:
            return jsonify({'success': False, 'message': 'Skill not found'}), 404

@app.route('/admin/users', methods=['GET'])
@handle_errors()
def admin_get_users():
    """Get all users for admin panel"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, created_at, 
                   CASE WHEN name LIKE '%BANNED%' THEN 0 ELSE 1 END as is_active 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
        
        return jsonify(users)

@app.route('/admin/users/<int:user_id>/ban', methods=['POST'])
@handle_errors()
def admin_ban_user(user_id):
    """Ban a user"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = CONCAT(name, ' (BANNED)') WHERE id = %s", (user_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'User banned successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/admin/swaps', methods=['GET'])
@handle_errors()
def admin_get_swaps():
    """Get all skill swap requests for admin panel"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                sr.id,
                sr.status,
                sr.created_at,
                u1.username as requester_name,
                u2.username as provider_name,
                s1.name as requested_skill,
                s2.name as offered_skill
            FROM skill_requests sr
            JOIN users u1 ON sr.requester_id = u1.id
            JOIN users u2 ON sr.provider_id = u2.id
            JOIN skills s1 ON sr.requested_skill_id = s1.id
            JOIN skills s2 ON sr.offered_skill_id = s2.id
            ORDER BY sr.created_at DESC
        """)
        swaps = cursor.fetchall()
        
        for swap in swaps:
            if swap['created_at']:
                swap['created_at'] = swap['created_at'].isoformat()
        
        return jsonify(swaps)

@app.route('/admin/ratings', methods=['GET'])
@handle_errors()
def admin_get_ratings():
    """Get all ratings for admin panel"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                r.id,
                r.rating,
                r.comment,
                r.created_at,
                u1.username as rater_name,
                u2.username as rated_user_name
            FROM ratings r
            JOIN users u1 ON r.rater_id = u1.id
            JOIN users u2 ON r.rated_user_id = u2.id
            ORDER BY r.created_at DESC
        """)
        ratings = cursor.fetchall()
        
        for rating in ratings:
            if rating['created_at']:
                rating['created_at'] = rating['created_at'].isoformat()
        
        return jsonify(ratings)

@app.route('/admin/send_message', methods=['POST'])
@handle_errors()
def admin_send_broadcast_message():
    """Send broadcast message to all users"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    data = validate_request_data(required_fields=['message'])
    message = data.get('message')
    title = data.get('title', 'Admin Broadcast')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all active users (not banned)
        cursor.execute("SELECT id FROM users WHERE name NOT LIKE '%BANNED%'")
        users = cursor.fetchall()
        
        if not users:
            return jsonify({'success': False, 'message': 'No active users found'}), 404
        
        # Send notification to each user
        for user in users:
            user_id = user[0]
            cursor.execute("""
                INSERT INTO notifications (user_id, type, title, message, is_read, created_at)
                VALUES (%s, 'message', %s, %s, FALSE, NOW())
            """, (user_id, title, message))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Broadcast message sent successfully to {len(users)} users',
            'users_notified': len(users)
        })

@app.route('/admin/download_reports', methods=['GET'])
@handle_errors()
def admin_download_reports():
    """Generate and download admin reports"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get comprehensive statistics
        cursor.execute("SELECT COUNT(*) as total_users FROM users WHERE is_active = 1")
        user_count = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as total_skills FROM skills")
        skills_count = cursor.fetchone()['total_skills']
        
        cursor.execute("SELECT COUNT(*) as total_swaps FROM skill_requests")
        swaps_count = cursor.fetchone()['total_swaps']
        
        cursor.execute("SELECT COUNT(*) as pending_swaps FROM skill_requests WHERE status = 'pending'")
        pending_swaps = cursor.fetchone()['pending_swaps']
        
        cursor.execute("SELECT COUNT(*) as completed_swaps FROM skill_requests WHERE status = 'accepted'")
        completed_swaps = cursor.fetchone()['completed_swaps']
        
        report_data = {
            'totalUsers': user_count,
            'totalSkills': skills_count,
            'totalSwaps': swaps_count,
            'pendingSwaps': pending_swaps,
            'completedSwaps': completed_swaps,
            'timestamp': datetime.datetime.now().isoformat(),
            'generatedBy': 'admin'
        }
        
        return jsonify({
            'success': True,
            'data': report_data
        })

@app.route('/notifications', methods=['GET'])
@handle_errors()
def get_user_notifications():
    """Get notifications for the logged-in user"""
    if 'user_id' not in session:
        raise AuthenticationException("Please log in to view notifications")
    
    user_id = session['user_id']
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, type, title, message, is_read, created_at
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 50
        """, (user_id,))
        notifications = cursor.fetchall()
        
        for notification in notifications:
            if notification['created_at']:
                notification['created_at'] = notification['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'notifications': notifications
        })

@app.route('/notifications/<int:notification_id>/read', methods=['POST'])
@handle_errors()
def mark_user_notification_read(notification_id):
    """Mark a notification as read"""
    if 'user_id' not in session:
        raise AuthenticationException("Please log in to update notifications")
    
    user_id = session['user_id']
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE id = %s AND user_id = %s
        """, (notification_id, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404

if __name__ == '__main__':
    app.run(debug=True)