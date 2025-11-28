# SETUP: Imports (For Flask)
from flask import Flask, request, jsonify
from flask_cors import CORS

# SETUP: Imports (For DB)
from dba import db, User, Appointment, Treatment, Department
from dba import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT
from authutils import create_token, require_auth, admin_required, doctor_required, patient_required
import bcrypt
from sqlalchemy.exc import IntegrityError  

# SETUP: Imports (Background Task Simulation)
import threading
import time

# INIT: Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/hms.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
CORS(app)

# INIT: Create tables and default admin user
with app.app_context():
    db.create_all()

    from dba import User, ROLE_ADMIN
    import bcrypt

    # only create if no admin exists yet
    existing_admin = User.query.filter_by(role=ROLE_ADMIN).first()
    if not existing_admin:
        pw_hash = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()

        admin = User(
            username="admin",
            name="Admin",
            email="admin@example.com",
            password_hash=pw_hash,
            role=ROLE_ADMIN,
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin / admin")
    else:
        print("Admin already exists, skipping seed.")


# ROUTE: Register patient
@app.post("/api/register")
def register():
    # INPUT
    data = request.json
    username = data["username"]
    email = data["email"]
    password = data["password"]
    name = data["name"]

    # PROCESS: Check existing user
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # PROCESS: Create user
    user = User(
        username=username,
        email=email,
        name=name,
        password_hash=pw_hash,
        role=ROLE_PATIENT,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered"})


# ROUTE: Login
@app.post("/api/login")
def login():
    # INPUT
    data = request.json
    username = data["username"]
    password = data["password"]

    # PROCESS
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 400

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid credentials"}), 400

    # OUTPUT
    token = create_token(user)
    return jsonify({"token": token, "role": user.role})


# ROUTE: Get profile
@app.get("/api/me")
@require_auth
def get_me():
    user = request.current_user
    return jsonify({
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


# ROUTE: Admin → Add doctor
@app.post("/api/admin/doctors")
@require_auth
@admin_required
def add_doctor():
    data = request.get_json()

    # INPUT: read fields
    username = data.get("username", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    specialization = data.get("specialization", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # PROCESS: hash password & create doctor
    from dba import User, ROLE_DOCTOR
    import bcrypt

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    doc = User(
        username=username,
        name=name,
        email=email,
        specialization=specialization,
        password_hash=pw_hash,
        role=ROLE_DOCTOR,
    )

    db.session.add(doc)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 400

    return jsonify(
        {
            "id": doc.id,
            "username": doc.username,
            "name": doc.name,
            "email": doc.email,
            "specialization": doc.specialization,
        }
    )



# ROUTE: Admin → List doctors
@app.get("/api/admin/doctors")
@require_auth
@admin_required
def list_doctors():
    doctors = User.query.filter_by(role=ROLE_DOCTOR).all()
    return jsonify([
        {
            "id": d.id, "name": d.name, "username": d.username,
            "email": d.email, "specialization": d.specialization
        } for d in doctors
    ])

# ROUTE: List doctors for any logged-in user
@app.get("/api/doctors")
@require_auth
def list_doctors_for_all():
    from dba import User, ROLE_DOCTOR

    docs = User.query.filter_by(role=ROLE_DOCTOR).all()
    data = []
    for d in docs:
        data.append(
            {
                "id": d.id,
                "username": d.username,
                "name": d.name,
                "email": d.email,
                "specialization": d.specialization,
            }
        )
    return jsonify(data)

# ROUTE: Patient → Book appointment
@app.post("/api/patient/appointments")
@require_auth
@patient_required
def book_app():
    user = request.current_user
    data = request.get_json() or {}

    raw_doctor_id = data.get("doctor_id")
    date = (data.get("date") or "").strip()
    time = (data.get("time") or "").strip()

    if not raw_doctor_id or not date or not time:
        return jsonify({"error": "Doctor, date and time are required"}), 400

    # doctor_id comes from JSON, so make sure it's an int
    try:
        doctor_id = int(raw_doctor_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid doctor"}), 400

    # make sure doctor actually exists and is a doctor
    doctor = User.query.get(doctor_id)
    if not doctor or doctor.role != ROLE_DOCTOR:
        return jsonify({"error": "Invalid doctor"}), 400

    # check if the slot is already taken for this doctor
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time=time
    ).first()
    if existing:
        return jsonify({"error": "This time slot is already booked"}), 400

    # create new appointment
    appt = Appointment(
        doctor_id=doctor_id,
        patient_id=user.id,
        date=date,
        time=time,
        status="Booked",
    )

    db.session.add(appt)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error booking appointment:", e)
        return jsonify(
            {"error": "Server error while booking appointment"}
        ), 500

    return jsonify(
        {
            "id": appt.id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
            "doctor_id": appt.doctor_id,
            "patient_id": appt.patient_id,
        }
    ), 201

# ROUTE: Patient → List own appointments
@app.get("/api/patient/appointments")
@require_auth
@patient_required
def list_patient_appointments():
    user = request.current_user
    from dba import Appointment, User

    appts = (
        Appointment.query.filter_by(patient_id=user.id)
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    result = []
    for a in appts:
        doctor = User.query.get(a.doctor_id)
        result.append(
            {
                "id": a.id,
                "date": a.date,
                "time": a.time,
                "status": a.status,
                
                "doctor_name": doctor.name if doctor else "",
                "doctor_username": doctor.username if doctor else "",
                "diagnosis": a.diagnosis,
                "prescription": a.prescription,
            }
        )

    return jsonify(result)

# ROUTE: Doctor → List own appointments
@app.get("/api/doctor/appointments")
@require_auth
@doctor_required
def list_doctor_appointments():
    user = request.current_user
    from dba import Appointment, User

    appts = (
        Appointment.query.filter_by(doctor_id=user.id)
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    result = []
    for a in appts:
        patient = User.query.get(a.patient_id)
        result.append(
            {
                "id": a.id,
                "date": a.date,
                "time": a.time,
                "status": a.status,
                "patient_name": patient.name if patient else "",
                "patient_username": patient.username if patient else "",
                "diagnosis": a.diagnosis,
                "prescription": a.prescription,
            }
        )

    return jsonify(result)

# ROUTE: Doctor → Update appointment
@app.put("/api/doctor/appointments/<int:aid>")
@require_auth
@doctor_required
def update_appt(aid):
    user = request.current_user
    from dba import Appointment

    data = request.get_json() or {}

    appt = Appointment.query.get_or_404(aid)

    # doctor can only edit own appointments
    if appt.doctor_id != user.id:
        return jsonify({"error": "Not allowed to modify this appointment"}), 403

    diagnosis = data.get("diagnosis", "").strip()
    prescription = data.get("prescription", "").strip()
    status = data.get("status", "").strip() or "Completed"

    appt.diagnosis = diagnosis
    appt.prescription = prescription
    appt.status = status

    db.session.commit()

    return jsonify(
        {
            "id": appt.id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
            "diagnosis": appt.diagnosis,
            "prescription": appt.prescription,
        }
    )

# ROUTE: Patient → Update own appointment (reschedule / cancel)
@app.put("/api/patient/appointments/<int:aid>")
@require_auth
@patient_required
def update_patient_appointment(aid):
    user = request.current_user

    # find appointment
    appt = Appointment.query.get_or_404(aid)
    if appt.patient_id != user.id:
        return jsonify({"error": "Not allowed to modify this appointment"}), 403

    data = request.get_json() or {}

    new_status = data.get("status")
    new_date = (data.get("date") or "").strip() if data.get("date") is not None else None
    new_time = (data.get("time") or "").strip() if data.get("time") is not None else None

    # If rescheduling (date/time change), check for conflicts
    if new_date or new_time:
        date = new_date or appt.date
        time = new_time or appt.time

        existing = (
            Appointment.query.filter(
                Appointment.doctor_id == appt.doctor_id,
                Appointment.date == date,
                Appointment.time == time,
                Appointment.id != appt.id,
            )
            .first()
        )
        if existing:
            return jsonify({"error": "This time slot is already booked"}), 400

        appt.date = date
        appt.time = time

    # If status change (e.g. cancel)
    if new_status:
        if new_status not in ["Booked", "Cancelled"]:
            return jsonify({"error": "Invalid status"}), 400
        appt.status = new_status

    db.session.commit()

    return jsonify(
        {
            "id": appt.id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
            "doctor_id": appt.doctor_id,
            "patient_id": appt.patient_id,
            "diagnosis": appt.diagnosis,
            "prescription": appt.prescription,
        }
    )

# ROUTE: Admin → List patients
@app.get("/api/admin/patients")
@require_auth
@admin_required
def admin_list_patients():
    patients = User.query.filter_by(role=ROLE_PATIENT).all()
    data = []
    for p in patients:
        data.append(
            {
                "id": p.id,
                "username": p.username,
                "name": p.name,
                "email": p.email,
            }
        )
    return jsonify(data)


# ROUTE: Admin → Summary counts
@app.get("/api/admin/summary")
@require_auth
@admin_required
def admin_summary():
    total_doctors = User.query.filter_by(role=ROLE_DOCTOR).count()
    total_patients = User.query.filter_by(role=ROLE_PATIENT).count()
    total_appointments = Appointment.query.count()

    booked = Appointment.query.filter_by(status="Booked").count()
    completed = Appointment.query.filter_by(status="Completed").count()
    cancelled = Appointment.query.filter_by(status="Cancelled").count()

    return jsonify(
        {
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "booked": booked,
            "completed": completed,
            "cancelled": cancelled,
        }
    )

# ROUTE: Admin → List all appointments
@app.get("/api/admin/appointments")
@require_auth
@admin_required
def admin_list_appointments():
    appts = Appointment.query.order_by(Appointment.date, Appointment.time).all()
    data = []
    for a in appts:
        doctor = User.query.get(a.doctor_id)
        patient = User.query.get(a.patient_id)
        data.append(
            {
                "id": a.id,
                "date": a.date,
                "time": a.time,
                "status": a.status,
                "doctor_name": doctor.name if doctor else "",
                "doctor_username": doctor.username if doctor else "",
                "patient_name": patient.name if patient else "",
                "patient_username": patient.username if patient else "",
                "diagnosis": a.diagnosis,
                "prescription": a.prescription,
            }
        )
    return jsonify(data)

# INIT: Background Task Simulation

def simulate_report_generation():
    import time
    time.sleep(3)
    print("Simulating heavy background processing...")
    with open("simulated_report.txt", "w") as f:
        f.write("Simulation complete.")

#ROUTE: Background Task Simulation
@app.get("/api/admin/run-simulation-task")
@require_auth
@admin_required
def run_simulation_task():
    thread = threading.Thread(target=simulate_report_generation)
    thread.start()

    return jsonify({
        "message": "Simulation started",
        "details": "A background simulation task is now running."
    })


@app.get("/api/admin/simulation-task-status")
@require_auth
@admin_required
def simulation_task_status():
    return jsonify({
        "status": "Simulation active",
        "note": "This background operation is a simulated task for demonstration."
    })


# MAIN
if __name__ == "__main__":
    app.run(debug=True)
