from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required
from routes.auth import role
from routes.auth import check_rls
import bcrypt
import pyodbc


caregivers_bp = Blueprint('caregivers', __name__)

@caregivers_bp.route('/caregivers', methods=['GET'])
@jwt_required()
@role('admin')
def get_caregivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caregivers")
    caregivers = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(caregivers)

@caregivers_bp.route('/caregivers/<phone_number>', methods=['GET'])
@jwt_required()
@role(['admin', 'caregiver'])
def get_caregiver(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM caregivers
        WHERE phone_number = ? 
    """, (phone_number))
    row = cursor.fetchone()
    conn.close()

    if row:
        caregiver = dict(zip([column[0] for column in cursor.description], row))
        check_rls(caregiver) 
        return jsonify(caregiver)
    return jsonify({'message': 'Caregiver not found'}), 404

@caregivers_bp.route('/caregivers', methods=['POST'])
@jwt_required()
@role('admin')
def add_caregiver():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO caregivers (first_name, last_name, phone_number, email, salary, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['first_name'], data['last_name'], data.get('phone_number'), data['email'], data['salary'], data['address']
    ))
    conn.commit()
    
    username = data.get('phone_number')
    password = data['last_name']
    
    role = "caregiver"
    caregiver_phone_number = data.get("phone_number")

    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, caregiver_phone_number) 
            VALUES (?, ?, ?, ?)
        """, (username, hashed_password, role, caregiver_phone_number))
        conn.commit()
        return jsonify({"message": "Caregiver registered successfully"}), 201
    except pyodbc.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

    conn.close()
    return jsonify({'message': 'Caregiver added successfully'}), 201

@caregivers_bp.route('/caregivers/<phone_number>', methods=['PUT'])
@jwt_required()
@role(['admin', 'caregiver'])
def update_caregiver(phone_number):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE caregivers
        SET salary = ?
        WHERE phone_number = ?
    """, (
        data.get('salary'),
        phone_number
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caregiver updated successfully'})

@caregivers_bp.route('/caregivers/<phone_number>', methods=['DELETE'])
@jwt_required()
@role('admin')
def delete_caregiver(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM caregivers WHERE phone_number = ? ", (phone_number))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caregiver deleted successfully'})

@caregivers_bp.route('/total-caregivers', methods=['GET'])
@jwt_required()
@role('admin')
def get_total_caregivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC GetTotalCaregivers")
    result = cursor.fetchone()
    conn.close()
    return jsonify({"total_caregivers": result[0]})
