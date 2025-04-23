from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required
from routes.auth import role
import bcrypt
import pyodbc
from datetime import date, datetime

residents_bp = Blueprint('residents', __name__)

def serialize_dates(record):
    for key, value in record.items():
        if isinstance(value, (date, datetime)):
            record[key] = value.strftime('%Y-%m-%d')  # or '%Y-%m-%d %H:%M:%S' for datetime
    return record

@residents_bp.route('/residents', methods=['GET'])
@jwt_required()
@role('admin')
def get_residents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM residents")
    residents = [serialize_dates(dict(zip([column[0] for column in cursor.description], row))) for row in cursor.fetchall()]

    conn.close()
    return jsonify(residents)

@residents_bp.route('/residents/<first_name>/<date_of_birth>', methods=['GET'])
@jwt_required()
@role(['admin', 'resident'])
def get_resident(first_name, date_of_birth):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM residents
        WHERE first_name = ? AND date_of_birth = ?
    """, (first_name, date_of_birth))
    row = cursor.fetchone()
    conn.close()

    if row:
        resident = dict(zip([column[0] for column in cursor.description], row))
        return jsonify(resident)
    return jsonify({'message': 'Resident not found'}), 404

@residents_bp.route('/residents', methods=['POST'])
@jwt_required()
@role('admin')
def add_resident():
    data = request.json
    
    conn = get_db_connection()
    
    username = data.get('phone_number')
    password = data['last_name']
    
    role = "resident"
    resident_first_name = data.get("first_name")
    resident_date_of_birth = data.get("date_of_birth")
    # caregiver_hire_date = data.get("caregiver_hire_date") if role == "caregiver" else None
        # return jsonify(username, password), 200
    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # conn = get_db_connection()
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
            INSERT INTO users (username, password_hash, role, resident_first_name, resident_date_of_birth) 
            VALUES (?, ?, ?, ?, ?)
        """, (username, hashed_password, role, resident_first_name, resident_date_of_birth))
        conn.commit()
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO residents (first_name, last_name, date_of_birth, gender, phone_number, address, emergency_contact_name, emergency_contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data['gender'], data.get('phone_number'),
            data.get('address'), data.get('emergency_contact_name'), data.get('emergency_contact_phone')
        ))
        conn.commit()
        
        return jsonify({"message": "Resident registered successfully"}), 201
    except pyodbc.IntegrityError as e:
        print(f"Database IntegrityError: {e}")
        return jsonify({"error": f": {str(e)}"}), 400
    finally:
        conn.close()

    conn.close()
    return jsonify({'message': 'Resident added successfully'}), 201

@residents_bp.route('/residents/<first_name>/<date_of_birth>', methods=['PUT'])
@jwt_required()
@role(['admin', 'resident'])
def update_resident(first_name, date_of_birth):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
            UPDATE residents
            SET gender = ?, 
                phone_number = ?, 
                address = ?, 
                emergency_contact_name = ?, 
                emergency_contact_phone = ?,  
                resident_status = ?, 
                last_name = ?
            WHERE first_name = ? AND date_of_birth = ?
        """, (
            data.get('gender'),
            data.get('phone_number'),
            data.get('address'),
            data.get('emergency_contact_name'),
            data.get('emergency_contact_phone'),
            data.get('resident_status', 'Active'),
            data.get('last_name'),  # last_name to update
            first_name,             # WHERE first_name
            date_of_birth           # WHERE date_of_birth
        ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resident updated successfully'})

@residents_bp.route('/residents/<first_name>/<date_of_birth>', methods=['DELETE'])
@jwt_required()
@role('admin')
def delete_resident(first_name, date_of_birth):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE first_name = ? AND date_of_birth = ?", (first_name, date_of_birth))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resident deleted successfully'})

@residents_bp.route('/total-residents', methods=['GET'])
@jwt_required()
@role('admin')
def get_total_residents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC GetTotalResidents")
    result = cursor.fetchone()
    conn.close()
    return jsonify({"total_residents": result[0]})


