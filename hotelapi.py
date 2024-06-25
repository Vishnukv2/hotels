from flask import Flask, request, jsonify
import pyodbc
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection parameters
server = '103.239.89.99,21433'
database = 'HospinsApp_DB_AE'
username = 'AE_Hospins_usr'
password = '7LNw37*Qm'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Global variable to store the count of connected users
connected_users_count = 0
count_lock = threading.Lock()

def get_db_connection():
    conn = pyodbc.connect(connection_string)
    return conn

@app.route('/add_guests', methods=['POST'])
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

@app.route('/connected_users', methods=['GET'])
def get_connected_users():
    global connected_users_count
    with count_lock:
        return jsonify({'connected_users': connected_users_count}), 200

def update_connected_users_count():
    global connected_users_count
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tbPMS_Guest WHERE isconnected = 1')
            row = cursor.fetchone()
            with count_lock:
                connected_users_count = row[0]
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error updating connected users count: {e}")
        time.sleep(3)  # Check every 3 seconds



@app.route('/update_checkout', methods=['PUT'])
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

@app.route('/update_room', methods=['PUT'])
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
    # Start the background thread to update connected users count
    thread = threading.Thread(target=update_connected_users_count)
    thread.daemon = True
    thread.start()
    app.run(debug=False)
