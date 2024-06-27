from flask import Flask, request, jsonify
import pyodbc
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={"/api/*": {"origins": "*"}})

# Database connection parameters
server = '103.239.89.99,21433'
database = 'HospinsApp_DB_AE'
username = 'AE_Hospins_usr'
password = '7LNw37*Qm'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    conn = pyodbc.connect(connection_string)
    return conn

@app.route('/api/add_guests', methods=['POST'])
def add_guest():
    data = request.json
    guest_name = data.get('GuestName')
    guest_email = data.get('GuestEmail')
    guest_mobile = data.get('GuestMobile')
    check_in = data.get('CheckIn')
    check_out = data.get('CheckOut')
    room_no = data.get('RoomNo')

    if not all([guest_name, guest_email, guest_mobile, check_in, check_out, room_no]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            INSERT INTO tbPMS_Guest (GuestName, GuestEmail, GuestMobile, CheckIn, CheckOut, RoomNo)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (guest_name, guest_email, guest_mobile, check_in, check_out, room_no))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'Guest added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/connected_users', methods=['GET'])
def get_connected_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT GuestName, RoomNo FROM tbPMS_Guest WHERE isconnected = 1')
        connected_users = [{'GuestName': row[0], 'RoomNo': row[1]} for row in cursor.fetchall()]
        total_connected_users = len(connected_users)
        cursor.close()
        conn.close()
        return jsonify({'Total connected users': total_connected_users, 'connected users via whatsapp': connected_users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_checkout', methods=['PUT'])
def update_checkout():
    data = request.json
    guest_name = data.get('GuestName')
    guest_mobile = data.get('GuestMobile')
    new_checkout = data.get('CheckOut')

    if not all([guest_name, guest_mobile, new_checkout]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            UPDATE tbPMS_Guest
            SET CheckOut = ?
            WHERE GuestName = ? AND GuestMobile = ?
        '''
        cursor.execute(query, (new_checkout, guest_name, guest_mobile))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Checkout date updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_room', methods=['PUT'])
def update_room():
    data = request.json
    guest_name = data.get('GuestName')
    guest_mobile = data.get('GuestMobile')
    new_room_no = data.get('RoomNo')

    if not all([guest_name, guest_mobile, new_room_no]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            UPDATE tbPMS_Guest
            SET RoomNo = ?
            WHERE GuestName = ? AND GuestMobile = ?
        '''
        cursor.execute(query, (new_room_no, guest_name, guest_mobile))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Room number updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
