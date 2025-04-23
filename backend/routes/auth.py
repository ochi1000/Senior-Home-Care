from flask import Blueprint, request, jsonify
from config.db import get_db_connection
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pyodbc
from functools import wraps


auth_bp = Blueprint('auth', __name__)

# Role-based access control example
def role(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt_identity()
            user_role = claims.get("role") if claims else None

            if not user_role or (isinstance(required_roles, list) and user_role not in required_roles) or (isinstance(required_roles, str) and user_role != required_roles):
                return jsonify({"msg": "Your role does not have access!"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

# 🔹 User Registration
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@role('admin')
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    role = data.get("role")
    # caregiver_first_name = data.get("caregiver_first_name") if role == "caregiver" else None
    # caregiver_last_name = data.get("caregiver_last_name") if role == "caregiver" else None
    # caregiver_hire_date = data.get("caregiver_hire_date") if role == "caregiver" else None

    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 Verify caregiver exists if registering as a caregiver
    # if role == "caregiver":
    #     cursor.execute("""
    #         SELECT 1 FROM caregivers 
    #         WHERE first_name = ? AND last_name = ? AND hire_date = ?
    #     """, (caregiver_first_name, caregiver_last_name, caregiver_hire_date))
    #     caregiver_exists = cursor.fetchone()
    #     if not caregiver_exists:
    #         return jsonify({"error": "Caregiver not found"}), 404

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role) 
            VALUES (?, ?, ?)
        """, (username, hashed_password, role))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except pyodbc.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()



# 🔹 User Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, password_hash, role, caregiver_phone_number, resident_first_name, resident_date_of_birth
        FROM users WHERE username = ?
    """, (username,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        access_token = create_access_token(identity={
            "user_id": user[0],
            "password_hash": user[1].decode('utf-8'),
            "role": user[2],
            "caregiver_phone_number": user[3],
            "resident_first_name": user[4],
            "resident_date_of_birth": user[5],
        })
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@jwt_required()
def check_rls(record_data):
    """
    Middleware-style function to check if the user has access to the record.
    `record_type`: 'resident' or 'caregiver'
    `record_data`: dict with keys relevant to identity (e.g. first_name, last_name, date_of_birth)
    """
    user = get_jwt_identity()  # Extract info from JWT

    record_type = user.get('role')

    #Admin access
    if record_type == 'admin':
        return None  # Admins can access all records
    
    # Resident access
    if record_type == 'resident':
        if (
            user.get('first_name') != record_data.get('first_name') or
            user.get('last_name') != record_data.get('last_name') or
            user.get('date_of_birth') != record_data.get('date_of_birth')
        ):
            return jsonify({"msg": "Access denied: You cannot access another resident’s data."}), 403

    # Caregiver access
    elif record_type == 'caregiver':
        if (
            user.get('phone_number') != record_data.get('phone_number')
        ):
            return jsonify({"msg": "Access denied: You cannot access another caregiver’s data."}), 403

    # If all checks pass
    return None