# SETUP: Imports
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# SETUP: Role constants
ROLE_ADMIN = "admin"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"


# MODEL: User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)

    specialization = db.Column(db.String(200))      # doctor use
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))

    appointments_as_patient = db.relationship(
        "Appointment", backref="patient", foreign_keys="Appointment.patient_id"
    )

    appointments_as_doctor = db.relationship(
        "Appointment", backref="doctor", foreign_keys="Appointment.doctor_id"
    )


# MODEL: Department
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.String(500))

    doctors = db.relationship("User", backref="department")


# MODEL: Appointment
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default="Booked")

    treatment = db.relationship("Treatment", backref="appointment", uselist=False)


# MODEL: Treatment
class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    diagnosis = db.Column(db.String(500))
    prescription = db.Column(db.String(500))
    notes = db.Column(db.String(500))
