from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

schedules_bp = Blueprint('schedules', __name__)

# Retrieve All Daily Schedules
@schedules_bp.route('/schedules', methods=['GET'])
def get_schedules():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules")
    schedules = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
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
