#SETUP : IMPORTS
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

#INIT : DATABASE
db = SQLAlchemy()

#MODEL : USER (Core identity for ALL roles)
class User(db.Model, UserMixin):
    #COLUMNS : KEYS & AUTH
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    #COLUMNS : ROLE & BASIC DETAILS
    # 1 = Admin, 2 = Doctor, 3 = Patient
    role = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)

    # (Kept from V1 so old code doesn’t explode;
    # Doctor-specific details will move to Doctor model)
    specialization = db.Column(db.String(120), nullable=True)

    #RELATIONSHIPS : APPOINTMENTS (V1-compatible)
    appointments = db.relationship(
        'Appointment',
        foreign_keys='[Appointment.patient_id]',
        backref='patient',
        lazy='dynamic'
    )

    doctor_appointments = db.relationship(
        'Appointment',
        foreign_keys='[Appointment.doctor_id]',
        backref='doctor',
        lazy='dynamic'
    )

    #RELATIONSHIPS : PROFILE EXTENSIONS (V2 models)
    doctor_profile = db.relationship(
        'Doctor',
        back_populates='user',
        uselist=False
    )

    patient_profile = db.relationship(
        'Patient',
        back_populates='user',
        uselist=False
    )

    def __repr__(self):
        return f"<User {self.username} - Role {self.role}>"

#MODEL : DOCTOR (V2 – extra metadata for doctors)
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # one-to-one with User row (role = Doctor)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    user = db.relationship('User', back_populates='doctor_profile')

    # domain-specific attributes
    specialization = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.String(255), nullable=True)  # could store JSON/text for slots
    is_active = db.Column(db.Boolean, default=True)          # blacklist / removed flag

    # optional: link to department
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    def __repr__(self):
        return f"<Doctor user_id={self.user_id} spec={self.specialization}>"

#MODEL : PATIENT (V2 – extra metadata for patients)
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # one-to-one with User row (role = Patient)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    user = db.relationship('User', back_populates='patient_profile')

    contact_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    emergency_contact = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f"<Patient user_id={self.user_id}>"

#MODEL : DEPARTMENT / SPECIALIZATION
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # doctors in this department
    doctors = db.relationship('Doctor', backref='department', lazy='dynamic')

    def __repr__(self):
        return f"<Department {self.name}>"

#MODEL : APPOINTMENT (kept V1 style but extended for V2)
class Appointment(db.Model):
    #COLUMNS : KEYS
    id = db.Column(db.Integer, primary_key=True)

    # still FK → user.id so old code/templates keep working
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #COLUMNS : DETAILS
    date = db.Column(db.String(50), nullable=False)  # YYYY-MM-DD
    time = db.Column(db.String(50), nullable=False)  # HH:MM

    status = db.Column(db.String(50), default='Booked')  # Booked / Completed / Cancelled

    # Optional link to department for reporting
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    department = db.relationship('Department', backref='appointments')

    #COLUMNS : TREATMENT (legacy V1 fields – will mirror into Treatment)
    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)

    #RELATIONSHIPS : TREATMENT HISTORY (V2)
    treatments = db.relationship('Treatment', backref='appointment', lazy='dynamic')

    def __repr__(self):
        return f"<Appointment {self.id} on {self.date}>"

#MODEL : TREATMENT (V2 – detailed treatment history)
class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)

    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Treatment appt={self.appointment_id} at {self.created_at}>"
