from flask import Blueprint, request, jsonify
from config.db import get_db_connection

caregivers_bp = Blueprint('caregivers', __name__)

@caregivers_bp.route('/caregivers', methods=['GET'])
def get_caregivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caregivers")
    caregivers = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(caregivers)

@caregivers_bp.route('/caregivers/<first_name>/<last_name>/<hire_date>', methods=['GET'])
def get_caregiver(first_name, last_name, hire_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM caregivers
        WHERE first_name = ? AND last_name = ? AND hire_date = ?
    """, (first_name, last_name, hire_date))
    row = cursor.fetchone()
    conn.close()

    if row:
        caregiver = dict(zip([column[0] for column in cursor.description], row))
        return jsonify(caregiver)
    return jsonify({'message': 'Caregiver not found'}), 404

@caregivers_bp.route('/caregivers', methods=['POST'])
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
    conn.close()
    return jsonify({'message': 'Caregiver added successfully'}), 201

@caregivers_bp.route('/caregivers/<first_name>/<last_name>/<hire_date>', methods=['PUT'])
def update_caregiver(first_name, last_name, hire_date):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE caregivers
        SET phone_number = ?, email = ?, position = ?, salary = ?
        WHERE first_name = ? AND last_name = ? AND hire_date = ?
    """, (
        data.get('phone_number'), data.get('email'), data.get('position'), data.get('salary'),
        first_name, last_name, hire_date
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caregiver updated successfully'})

@caregivers_bp.route('/caregivers/<first_name>/<last_name>/<hire_date>', methods=['DELETE'])
def delete_caregiver(first_name, last_name, hire_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM caregivers WHERE first_name = ? AND last_name = ? AND hire_date = ?", (first_name, last_name, hire_date))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caregiver deleted successfully'})
