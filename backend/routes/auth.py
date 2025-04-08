from flask import Blueprint, request, jsonify
from config.db import get_db_connection
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pyodbc


auth_bp = Blueprint('auth', __name__)

# 🔹 User Registration
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    role = data.get("role")
    caregiver_first_name = data.get("caregiver_first_name") if role == "caregiver" else None
    caregiver_last_name = data.get("caregiver_last_name") if role == "caregiver" else None
    caregiver_hire_date = data.get("caregiver_hire_date") if role == "caregiver" else None

    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 Verify caregiver exists if registering as a caregiver
    if role == "caregiver":
        cursor.execute("""
            SELECT 1 FROM caregivers 
            WHERE first_name = ? AND last_name = ? AND hire_date = ?
        """, (caregiver_first_name, caregiver_last_name, caregiver_hire_date))
        caregiver_exists = cursor.fetchone()
        if not caregiver_exists:
            return jsonify({"error": "Caregiver not found"}), 404

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, caregiver_first_name, caregiver_last_name, caregiver_hire_date) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, hashed_password, role, caregiver_first_name, caregiver_last_name, caregiver_hire_date))
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
        SELECT user_id, password_hash, role, caregiver_first_name, caregiver_last_name, caregiver_hire_date
        FROM users WHERE username = ?
    """, (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        access_token = create_access_token(identity={
            "user_id": user[0], 
            "role": user[2], 
            "caregiver_first_name": user[3], 
            "caregiver_last_name": user[4], 
            "caregiver_hire_date": user[5]
        })
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401
