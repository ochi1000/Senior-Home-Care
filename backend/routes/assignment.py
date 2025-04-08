from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from datetime import datetime
import sys

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/assignments', methods=['GET'])
def get_assignments():
    """Retrieve all resident-caregiver assignments with resident and caregiver details."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        rc.resident_first_name,
        r.last_name AS resident_last_name,
        rc.resident_date_of_birth,
        r.gender,
        r.phone_number AS resident_phone,
        r.address AS resident_address,
        c.first_name AS caregiver_first_name,
        c.last_name AS caregiver_last_name,
        c.phone_number AS caregiver_phone,
        rc.assignment_status,
        rc.assignment_end_date
    FROM resident_caregivers rc
    JOIN residents r
        ON rc.resident_first_name = r.first_name
        AND rc.resident_date_of_birth = r.date_of_birth
    JOIN caregivers c
        ON rc.caregiver_phone_number = c.phone_number
    """

    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    assignments = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(assignments)


@assignments_bp.route('/assignments/<resident_first_name>/<resident_last_name>/<resident_date_of_birth>/<caregiver_first_name>/<caregiver_last_name>/<caregiver_hire_date>', methods=['GET'])
def get_assignment(resident_first_name, resident_last_name, resident_date_of_birth, caregiver_first_name, caregiver_last_name, caregiver_hire_date):
    """Retrieve a specific resident-caregiver assignment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM resident_caregivers
        WHERE resident_first_name = ? AND resident_last_name = ? AND resident_date_of_birth = ?
        AND caregiver_first_name = ? AND caregiver_last_name = ? AND caregiver_hire_date = ?
    """, (resident_first_name, resident_last_name, resident_date_of_birth, caregiver_first_name, caregiver_last_name, caregiver_hire_date))
    row = cursor.fetchone()
    conn.close()

    if row:
        assignment = dict(zip([column[0] for column in cursor.description], row))
        return jsonify(assignment)
    return jsonify({'message': 'Assignment not found'}), 404

@assignments_bp.route('/assignments', methods=['POST'])
def add_assignment():
    """Create a new resident-caregiver assignment."""
    data = request.json
    # print(data['resident_date_of_birth'], file=sys.stderr)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resident_caregivers (resident_first_name, resident_date_of_birth, caregiver_phone_number)
        VALUES (?, ?, ?)
    """, (data['resident_first_name'], data['resident_date_of_birth'], data['caregiver_phone_number']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Assignment added successfully'}), 201

@assignments_bp.route('/assignments/<resident_first_name>/<resident_last_name>/<resident_date_of_birth>/<caregiver_first_name>/<caregiver_last_name>/<caregiver_hire_date>', methods=['DELETE'])
def delete_assignment(resident_first_name, resident_last_name, resident_date_of_birth, caregiver_first_name, caregiver_last_name, caregiver_hire_date):
    """Delete a resident-caregiver assignment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM resident_caregivers
        WHERE resident_first_name = ? AND resident_last_name = ? AND resident_date_of_birth = ?
        AND caregiver_first_name = ? AND caregiver_last_name = ? AND caregiver_hire_date = ?
    """, (resident_first_name, resident_last_name, resident_date_of_birth, caregiver_first_name, caregiver_last_name, caregiver_hire_date))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Assignment deleted successfully'})
