from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from datetime import time, date, datetime

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/schedules', methods=['GET'])
def get_schedules():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
            """)
    rows = cursor.fetchall()

    # Get column names
    columns = [column[0] for column in cursor.description]

    # Convert time objects to strings
    schedules = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        for key, value in row_dict.items():
            if isinstance(value, time):
                row_dict[key] = value.strftime('%H:%M:%S')
        schedules.append(row_dict)

    conn.close()
    return jsonify(schedules), 200
    
# Retrieve All Daily Schedules
@schedules_bp.route('/schedulesw', methods=['GET'])
@jwt_required()
def get_schedulesw():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    identity = get_jwt_identity()
    user_role = identity.get('role')
    caregiver_phone_number = identity.get('caregiver_phone_number')
    resident_first_name = identity.get('resident_first_name')
    resident_date_of_birth = identity.get('resident_date_of_birth')
    
    resident_date_of_birth = datetime.strptime(resident_date_of_birth, "%a, %d %b %Y %H:%M:%S GMT")

    # Format the datetime object to 'YYYY-MM-DD'
    resident_date_of_birth = resident_date_of_birth.strftime("%Y-%m-%d")
            
    if user_role == 'caregiver':
        cursor.execute("""
            SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
            WHERE c.phone_number = ?
        """, (caregiver_phone_number,))

    elif user_role == 'resident':
        cursor.execute("""
            SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
            WHERE r.first_name = ? AND r.date_of_birth = ?
        """, (resident_first_name, resident_date_of_birth))

    elif user_role == 'admin':
        cursor.execute("""
            SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
        """)
    else:
        return jsonify({"msg": "Unauthorized role!"}), 403
    
    rows = cursor.fetchall()
    # Get column names
    columns = [column[0] for column in cursor.description]

    # Convert time objects to strings
    schedules = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        for key, value in row_dict.items():
            if isinstance(value, time):
                row_dict[key] = value.strftime('%H:%M:%S')
        schedules.append(row_dict)

    conn.close()
    return jsonify(schedules), 200


# Sign-In: Check-in address & Shift Start
@schedules_bp.route('/schedules/sign-in', methods=['POST'])
@jwt_required()
def sign_in():
    user = get_jwt_identity()
    if user["role"] != "caregiver":
        return jsonify({"error": "Access denied"}), 403

    # Ensure caregivers can only sign in for their own schedules
    data = request.json
    schedule_id = data.get("schedule_id")
    check_in_address = data.get("check_in_address")
    shift_start = data.get("shift_start")

    if not all([schedule_id, check_in_address, shift_start]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate the caregiver is assigned to this schedule
    cursor.execute("""
        SELECT 1 FROM schedules
        WHERE schedule_id = ? AND caregiver_first_name = ? AND caregiver_last_name = ? AND caregiver_hire_date = ?
    """, (schedule_id, user["caregiver_first_name"], user["caregiver_last_name"], user["caregiver_hire_date"]))
    assigned_schedule = cursor.fetchone()

    if not assigned_schedule:
        return jsonify({"error": "You are not assigned to this schedule"}), 403

    # Update schedule
    cursor.execute("""
        UPDATE schedules
        SET check_in_address = ?, shift_start = ?
        WHERE schedule_id = ?
    """, (check_in_address, shift_start, schedule_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Signed in successfully"}), 200



# Update Notes
@schedules_bp.route('/schedules/update-notes', methods=['PUT'])
def update_notes():
    data = request.json
    schedule_id = data.get("schedule_id")
    notes = data.get("notes")

    if not all([schedule_id, notes]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedules
        SET notes = ?
        WHERE schedule_id = ?
    """, (notes, schedule_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Notes updated successfully"}), 200


# Sign-Out: Shift End & Check-Out Address
@schedules_bp.route('/schedules/sign-out', methods=['POST'])
def sign_out():
    data = request.json
    schedule_id = data.get("schedule_id")
    shift_end = data.get("shift_end")
    check_out_address = data.get("check_out_address")

    if not all([schedule_id, shift_end, check_out_address]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedules
        SET shift_end = ?, check_out_address = ?
        WHERE schedule_id = ?
    """, (shift_end, check_out_address, schedule_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Signed out successfully"}), 200


@schedules_bp.route('/schedules/user', methods=['GET'])
@jwt_required()
def get_user_schedules():
    identity = get_jwt_identity()
    user_role = identity.get('role')
    caregiver_phone_number = identity.get('caregiver_phone_number')
    resident_first_name = identity.get('resident_first_name')
    resident_date_of_birth = identity.get('resident_date_of_birth')

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_role == 'caregiver':
        cursor.execute("""
            SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
            WHERE c.phone_number = ?
        """, (caregiver_phone_number,))

    elif user_role == 'resident':
        cursor.execute("""
            SELECT 
                s.*, 
                CONCAT(c.first_name, ' ', c.last_name) AS caregiver_name,
                CONCAT(r.first_name, ' ', r.last_name) AS resident_name
            FROM schedules s
            LEFT JOIN caregivers c
                ON s.caregiver_phone_number = c.phone_number
            LEFT JOIN residents r
                ON s.resident_first_name = r.first_name 
                AND s.resident_date_of_birth = r.date_of_birth
            WHERE r.first_name = ? AND r.date_of_birth = ?
        """, (resident_first_name, resident_date_of_birth))
    else:
        return jsonify({"msg": "Unauthorized role!"}), 403

    schedules = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(schedules), 200