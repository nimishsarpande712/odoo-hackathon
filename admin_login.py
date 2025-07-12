# Admin Login
# Handles admin authentication

from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
        return jsonify({"message": "Login successful", "token": "mock_token"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(port=3000, debug=True)
