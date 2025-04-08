from flask import Blueprint, request, jsonify
from config.db import get_db_connection

services_bp = Blueprint('services', __name__)

@services_bp.route('/services', methods=['GET'])
def get_services():
    """Retrieve all services."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services")
    services = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(services)

@services_bp.route('/services/<service_name>', methods=['GET'])
def get_service(service_name):
    """Retrieve a single service by primary key (service_name)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE service_name = ?", (service_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        service = dict(zip([column[0] for column in cursor.description], row))
        return jsonify(service)
    return jsonify({'message': 'Service not found'}), 404

@services_bp.route('/services', methods=['POST'])
def add_service():
    """Create a new service."""
    data = request.json
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO services (service_name, description, cost)
        VALUES (?, ?, ?)
    """, (data['service_name'], data.get('description', ''), data['cost']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Service added successfully'}), 201

@services_bp.route('/services/<service_name>', methods=['PUT'])
def update_service(service_name):
    """Update an existing service."""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE services
        SET description = ?, cost = ?
        WHERE service_name = ?
    """, (data.get('description', ''), data['cost'], service_name))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Service updated successfully'})

@services_bp.route('/services/<service_name>', methods=['DELETE'])
def delete_service(service_name):
    """Delete a service."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services WHERE service_name = ?", (service_name,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Service deleted successfully'})
