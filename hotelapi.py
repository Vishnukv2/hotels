from flask import Flask, request, jsonify
import pyodbc
import threading
import time
import requests
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
        cursor.execute('SELECT GuestName FROM tbPMS_Guest WHERE isconnected = 1')
        connected_users = [row[0] for row in cursor.fetchall()]
        total_connected_users = len(connected_users)
        cursor.close()
        conn.close()

        # Construct the response message
        response_message = f"Guests connected via WhatsApp: {total_connected_users},\n"
        response_message += "\n".join(connected_users)

        return jsonify(response_message), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_checkout', methods=['PUT'])
def update_checkout():
    data = request.json
    room_no = data.get('RoomNo')
    new_checkout = data.get('CheckOut')

    if not all([room_no, new_checkout]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            UPDATE tbPMS_Guest
            SET CheckOut = ?
            WHERE RoomNo = ?
        '''
        cursor.execute(query, (new_checkout, room_no))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Checkout date updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_room', methods=['PUT'])
def update_room():
    data = request.json
    current_room_no = data.get('CurrentRoomNo')
    new_room_no = data.get('RoomNo')

    if not all([current_room_no, new_room_no]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            UPDATE tbPMS_Guest
            SET RoomNo = ?
            WHERE RoomNo = ?
        '''
        cursor.execute(query, (new_room_no, current_room_no))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Room number updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_welcome_message', methods=['POST'])
def send_welcome_message():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 1 GuestName, RoomNo, CheckIn, CheckOut, GuestMobile
            FROM tbPMS_Guest
            ORDER BY CreatedDate DESC
        ''')
        guest = cursor.fetchone()
        if not guest:
            return jsonify({'error': 'No guests found in the database'}), 404

        guest_name, room_no, check_in, check_out, guest_mobile = guest

        message = (
            f"Hello {guest_name}. Welcome to Aloft Palm Jumeirah! I am your personal eButler Bruce. "
            f"You have checked in to room number {room_no} on {check_in} and scheduled for checkout on {check_out}. "
            f"Hope you have a wonderful stay!"
        )

        # Send the message via WhatsApp API
        whatsapp_api_url = "https://api.whatsapp.wayschimp.com/send-custom-message"
        payload = {
            "recipient": guest_mobile,
            "text": message
        }
        response = requests.post(whatsapp_api_url, json=payload)
        if response.status_code == 200:
            return jsonify({'message': 'Welcome message sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send message'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
