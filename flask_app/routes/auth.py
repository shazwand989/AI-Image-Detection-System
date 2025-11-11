"""
Authentication routes - Register and Login
Matches Node.js auth.js functionality with JWT and bcrypt
"""
import os
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta
from database import execute_query
from functools import wraps

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
REG_SECRET = os.getenv('REG_SECRET', 'replace_with_strong_reg_secret')

def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    reg_secret = data.get('reg_secret', '')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    # Check if username already exists
    existing = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if existing:
        return jsonify({'message': 'Username already exists'}), 409
    
    # Check admin secret if creating admin
    final_role = 'user'
    if role == 'admin':
        if reg_secret != REG_SECRET:
            return jsonify({'message': 'Invalid admin registration secret'}), 403
        final_role = 'admin'
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert new user
    user_id = execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, password_hash, final_role)
    )
    
    if user_id:
        return jsonify({
            'message': 'Account created successfully',
            'id': user_id
        }), 201
    else:
        return jsonify({'message': 'Failed to create account'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    # Get user from database
    user = execute_query(
        "SELECT id, username, password_hash, role FROM users WHERE username = %s",
        (username,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Verify password
    password_match = bcrypt.checkpw(
        password.encode('utf-8'),
        user['password_hash'].encode('utf-8')
    )
    
    if not password_match:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create JWT token
    payload = {
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=8)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    }), 200
