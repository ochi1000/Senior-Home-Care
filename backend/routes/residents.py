from flask import Blueprint, request, jsonify
from config.db import get_db_connection

residents_bp = Blueprint('residents', __name__)

@residents_bp.route('/residents', methods=['GET'])
def get_residents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM residents")
    residents = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(residents)

@residents_bp.route('/residents/<first_name>/<last_name>/<date_of_birth>', methods=['GET'])
def get_resident(first_name, last_name, date_of_birth):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM residents
        WHERE first_name = ? AND last_name = ? AND date_of_birth = ?
    """, (first_name, last_name, date_of_birth))
    row = cursor.fetchone()
    conn.close()

    if row:
        resident = dict(zip([column[0] for column in cursor.description], row))
        return jsonify(resident)
    return jsonify({'message': 'Resident not found'}), 404


@residents_bp.route('/residents', methods=['POST'])
def add_resident():
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO residents (first_name, last_name, date_of_birth, gender, phone_number, address, emergency_contact_name, emergency_contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['first_name'], data['last_name'], data['date_of_birth'], data['gender'], data.get('phone_number'),
        data.get('address'), data.get('emergency_contact_name'), data.get('emergency_contact_phone')
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resident added successfully'}), 201

@residents_bp.route('/residents/<first_name>/<last_name>/<date_of_birth>', methods=['PUT'])
def update_resident(first_name, last_name, date_of_birth):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE residents
        SET gender = ?, phone_number = ?, address = ?, emergency_contact_name = ?, emergency_contact_phone = ?, admission_date = ?, status = ?
        WHERE first_name = ? AND last_name = ? AND date_of_birth = ?
    """, (
        data.get('gender'), data.get('phone_number'), data.get('address'), data.get('emergency_contact_name'),
        data.get('emergency_contact_phone'), data.get('admission_date'), data.get('status', 'Active'),
        first_name, last_name, date_of_birth
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resident updated successfully'})

@residents_bp.route('/residents/<first_name>/<last_name>/<date_of_birth>', methods=['DELETE'])
def delete_resident(first_name, last_name, date_of_birth):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE first_name = ? AND last_name = ? AND date_of_birth = ?", (first_name, last_name, date_of_birth))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resident deleted successfully'})
