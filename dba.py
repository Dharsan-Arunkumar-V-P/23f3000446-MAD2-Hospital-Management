#SETUP : IMPORTS
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

#INIT : DATABASE
db = SQLAlchemy()

#MODEL : USER
class User(db.Model, UserMixin):
    #COLUMNS : KEYS & AUTH
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=True)

    #COLUMNS : ROLE & DETAILS
    role = db.Column(db.Integer, nullable=False) 
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=True) 
    
    #RELATIONSHIPS : APPOINTMENTS
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

    def __repr__(self):
        return f"<User {self.username} - Role {self.role}>"

#MODEL : APPOINTMENT
class Appointment(db.Model):
    #COLUMNS : KEYS
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
    #COLUMNS : DETAILS
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False) 
    status = db.Column(db.String(50), default='Booked') 
    
    #COLUMNS : TREATMENT
    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<Appointment {self.id} on {self.date}>"