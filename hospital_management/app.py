from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
from database import get_db_connection, close_connection

app = Flask(__name__)
CORS(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'        # your MySQL password
app.config['MYSQL_DB'] = 'hospital_db'   # your database name

mysql = MySQL(app)


# ==================== PAGE ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients_page():
    return render_template('patients.html')

@app.route('/doctors')
def doctors_page():
    return render_template('doctors.html')

@app.route('/appointments')
def appointments_page():
    return render_template('appointments.html')


# ==================== PATIENT API ====================

@app.route('/api/patients', methods=['GET'])
def get_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = cursor.fetchall()
    cursor.close()
    close_connection(conn)
    return jsonify(patients)


@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO patients
        (first_name, last_name, date_of_birth, gender, phone, email, address, blood_group)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data.get('first_name'),
        data.get('last_name'),
        data.get('date_of_birth'),
        data.get('gender'),
        data.get('phone'),
        data.get('email'),
        data.get('address'),
        data.get('blood_group')
    )

    cursor.execute(query, values)
    conn.commit()

    patient_id = cursor.lastrowid

    cursor.close()
    close_connection(conn)

    return jsonify({
        'message': 'Patient added successfully',
        'patient_id': patient_id
    }), 201


@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE patient_id = %s",
        (patient_id,)
    )

    conn.commit()

    cursor.close()
    close_connection(conn)

    return jsonify({'message': 'Patient deleted successfully'})


# ==================== DOCTOR API ====================

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM doctors ORDER BY created_at DESC")
    doctors = cursor.fetchall()

    cursor.close()
    close_connection(conn)

    return jsonify(doctors)


@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO doctors
        (first_name, last_name, specialization, phone, email, experience_years, consultation_fee, available_days)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data.get('first_name'),
        data.get('last_name'),
        data.get('specialization'),
        data.get('phone'),
        data.get('email'),
        data.get('experience_years'),
        data.get('consultation_fee'),
        data.get('available_days')
    )

    cursor.execute(query, values)
    conn.commit()

    doctor_id = cursor.lastrowid

    cursor.close()
    close_connection(conn)

    return jsonify({
        'message': 'Doctor added successfully',
        'doctor_id': doctor_id
    }), 201


# ==================== APPOINTMENT API ====================

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments with patient and doctor names"""
    try:
        conn = get_db_connection()
        
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                a.appointment_id,
                a.patient_id,
                a.doctor_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.reason,
                a.notes,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                d.specialization
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        
        cursor.execute(query)
        appointments = cursor.fetchall()
        
        # Convert date and time objects to strings
        for apt in appointments:
            if apt['appointment_date']:
                apt['appointment_date'] = str(apt['appointment_date'])
            if apt['appointment_time']:
                apt['appointment_time'] = str(apt['appointment_time'])
        
        cursor.close()
        close_connection(conn)
        
        print(f"Found {len(appointments)} appointments")  # Debug log
        return jsonify(appointments)
        
    except Exception as e:
        print(f"Error in get_appointments: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500





@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    """Add new appointment"""
    try:
        data = request.json
        conn = get_db_connection()
        
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        query = """
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            data['patient_id'], 
            data['doctor_id'], 
            data['appointment_date'], 
            data['appointment_time'],
            data.get('reason', '')  # Use .get() to handle missing reason
        )
        
        cursor.execute(query, values)
        conn.commit()
        appointment_id = cursor.lastrowid
        
        cursor.close()
        close_connection(conn)
        
        print(f"Appointment {appointment_id} created successfully")  # Debug log
        return jsonify({
            'message': 'Appointment scheduled successfully', 
            'appointment_id': appointment_id
        }), 201
        
    except Exception as e:
        print(f"Error in add_appointment: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status = %s WHERE appointment_id = %s",
        (data.get('status'), appointment_id)
    )

    conn.commit()

    cursor.close()
    close_connection(conn)

    return jsonify({'message': 'Appointment updated successfully'})


# ==================== DASHBOARD STATS ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS count FROM patients")
    total_patients = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM doctors")
    total_doctors = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM appointments WHERE status = 'Scheduled'")
    pending_appointments = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM appointments WHERE DATE(appointment_date) = CURDATE()")
    today_appointments = cursor.fetchone()['count']

    cursor.close()
    close_connection(conn)

    return jsonify({
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'pending_appointments': pending_appointments,
        'today_appointments': today_appointments
    })

@app.route("/test-db")
def test_db():
    try:
        cursor = mysql.connection.cursor()
        return "Database connected successfully!"
    except Exception as e:
        return f"DB ERROR: {e}"



if __name__ == '__main__':
    app.run(debug=True, port=5000)
