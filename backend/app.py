# SETUP: Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
from dba import db, User, Appointment, Treatment, Department
from dba import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT
from authutils import create_token, require_auth, admin_required, doctor_required, patient_required
import bcrypt
from sqlalchemy.exc import IntegrityError  


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
    # INPUT: current user & request data
    user = request.current_user
    data = request.get_json() or {}

    doctor_id = data.get("doctor_id")
    date = data.get("date")
    time = data.get("time")

    if not doctor_id or not date or not time:
        return jsonify({"error": "Doctor, date and time are required"}), 400

    from dba import Appointment

    # PROCESS: check if the slot is already taken for this doctor
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time=time
    ).first()

    if existing:
        return jsonify({"error": "This time slot is already booked"}), 400

    # PROCESS: create new appointment
    appt = Appointment(
        doctor_id=doctor_id,
        patient_id=user.id,
        date=date,
        time=time,
        status="Booked",
    )

    db.session.add(appt)
    db.session.commit()

    return jsonify(
        {
            "id": appt.id,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status,
        }
    )

# ROUTE: Patient → List own appointments
@app.get("/api/patient/appointments")
@require_auth
@patient_required
def list_patient_appointments():
    user = request.current_user

    appts = Appointment.query.filter_by(patient_id=user.id).all()

    data = []
    for a in appts:
        data.append({
            "id": a.id,
            "date": a.date,
            "time": a.time,
            "status": a.status,
            "doctor_name": a.doctor.name if a.doctor else None
        })

    return jsonify(data)

# ROUTE: Doctor → List own appointments
@app.get("/api/doctor/appointments")
@require_auth
@doctor_required
def list_doctor_appointments():
    user = request.current_user

    appts = Appointment.query.filter_by(doctor_id=user.id).all()

    data = []
    for a in appts:
        data.append({
            "id": a.id,
            "date": a.date,
            "time": a.time,
            "status": a.status,
            "patient_name": a.patient.name if a.patient else None
        })

    return jsonify(data)

# ROUTE: Doctor → Update appointment
@app.put("/api/doctor/appointments/<int:aid>")
@require_auth
@doctor_required
def update_appt(aid):
    appt = Appointment.query.get(aid)
    if not appt:
        return jsonify({"error": "Not found"}), 404

    data = request.json

    treatment = Treatment(
        appointment_id=aid,
        diagnosis=data["diagnosis"],
        prescription=data["prescription"],
        notes=data["notes"]
    )

    db.session.add(treatment)
    db.session.commit()

    return jsonify({"message": "Updated"})


# MAIN
if __name__ == "__main__":
    app.run(debug=True)
