#SETUP : IMPORTS
from flask import Flask, render_template, request, redirect, url_for, flash
from dba import db, User, Appointment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from sqlalchemy import or_
import datetime

#CONSTANTS : USER ROLES
ROLE_ADMIN = 1
ROLE_DOCTOR = 2
ROLE_PATIENT = 3


#UTILITY : HELPER FUNCTIONS
def getRoleName(roleID):
    if roleID == ROLE_ADMIN:
        return 'Admin'
    if roleID == ROLE_DOCTOR:
        return 'Doctor'
    if roleID == ROLE_PATIENT:
        return 'Patient'
    return 'Unknown'


def adminRequired(func):
    @wraps(func)
    def checkAdminRole(*args, **kwargs):
        # PROCESS: Enforce Admin role (1) access
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            # OUTPUT: Block access
            flash('Access denied: Admin privileges required.', 'danger')
            return redirect(url_for('dashboardPage'))
        return func(*args, **kwargs)
    return checkAdminRole


#FACTORY : CREATE APP
def createApp():
    appObj = Flask(__name__)

    #CONFIG : APP SETTINGS
    appObj.config.update({
        'SECRET_KEY': 'your_super_secret_key_change_me',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    #INIT : EXTENSIONS
    db.init_app(appObj)
    bCryptObj = Bcrypt(appObj)

    loginManager = LoginManager()
    loginManager.init_app(appObj)
    loginManager.login_view = 'loginUser'

    #SETUP : USER LOADER
    @loginManager.user_loader
    def loadUser(userID):
        return User.query.get(int(userID))

    #INIT : DATABASE
    with appObj.app_context():
        # PROCESS: Create all database tables
        db.create_all()
        print("Database tables ensured.")

        # PROCESS: Create default Super Admin (Role 1) if not found
        if User.query.filter_by(role=ROLE_ADMIN).first() is None:
            adminPassHashed = bCryptObj.generate_password_hash('admin_pass').decode('utf-8')
            adminUser = User(
                username='admin',
                password=adminPassHashed,
                role=ROLE_ADMIN,
                name='Super Admin',
                email='admin@hospital.com'
            )
            db.session.add(adminUser)
            db.session.commit()
            print("Default Admin created. Username: admin, Password: admin_pass")

    #SETUP : CONTEXT PROCESSOR
    @appObj.context_processor
    def injectUserData():
        if current_user.is_authenticated:
            # OUTPUT: User context variables
            return {
                'currentUserRole': getRoleName(current_user.role),
                'currentUserNAME': current_user.name,
                'roleID': current_user.role
            }
        return {'currentUserRole': None, 'currentUserNAME': None, 'roleID': None}

    #ROUTE : AUTHENTICATION

    @appObj.route('/')
    def indexPage():
        if current_user.is_authenticated:
            return redirect(url_for('dashboardPage'))
        return render_template('login.html')

    @appObj.route('/login', methods=['GET', 'POST'])
    def loginUser():
        if current_user.is_authenticated:
            return redirect(url_for('dashboardPage'))

        if request.method == 'POST':
            # INPUT: Get credentials
            userName = request.form.get('username')
            userPass = request.form.get('password')
            userObj = User.query.filter_by(username=userName).first()

            # PROCESS: Verify user AND password (Bcrypt check)
            if userObj and bCryptObj.check_password_hash(userObj.password, userPass):
                login_user(userObj)
                flash(f'Login successful! Welcome, {userObj.name}.', 'success')
                # OUTPUT: Redirect on success
                return redirect(url_for('dashboardPage'))
            else:
                # OUTPUT: Flash error
                flash('Login failed. Check username and password.', 'danger')

        # OUTPUT: Render login form
        return render_template('login.html')

    @appObj.route('/registerPatient', methods=['GET', 'POST'])
    def registerPatient():
        if current_user.is_authenticated:
            return redirect(url_for('dashboardPage'))

        if request.method == 'POST':
            # INPUT: Get form data
            userName = request.form.get('username')
            userPass = request.form.get('password')
            fullName = request.form.get('name')

            # PROCESS 1: Check for existing user
            if User.query.filter_by(username=userName).first():
                flash('Username already taken. Choose another.', 'danger')
                return render_template('register.html')

            # PROCESS 2: Hash password and save new Patient (Role 3)
            passHashed = bCryptObj.generate_password_hash(userPass).decode('utf-8')
            newUser = User(
                username=userName,
                password=passHashed,
                role=ROLE_PATIENT,
                name=fullName,
                email=f"{userName}@patient.com"
            )

            db.session.add(newUser)
            db.session.commit()

            # OUTPUT: Redirect to login page
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('loginUser'))

        # OUTPUT: Render registration form
        return render_template('register.html')

    @appObj.route('/dashboard')
    @login_required
    def dashboardPage():
        # PROCESS 1: Prepare role-specific data
        totalDoctors = totalPatients = totalAppts = None
        departments = None

        if current_user.role == ROLE_ADMIN:
            # Admin: counts for summary cards
            totalDoctors = User.query.filter_by(role=ROLE_DOCTOR).count()
            totalPatients = User.query.filter_by(role=ROLE_PATIENT).count()
            totalAppts = Appointment.query.count()

        elif current_user.role == ROLE_PATIENT:
            # Patient: list available specializations/departments
            specs = (
                db.session.query(User.specialization)
                .filter(User.role == ROLE_DOCTOR)
                .distinct()
                .all()
            )
            departments = [s[0] for s in specs if s[0]]

        # OUTPUT: Render dashboard with extra context
        return render_template(
            'dashboard.html',
            totalDoctors=totalDoctors,
            totalPatients=totalPatients,
            totalAppts=totalAppts,
            departments=departments
        )

    @appObj.route('/logout')
    @login_required
    def logoutUser():
        # PROCESS: End session
        logout_user()
        # OUTPUT: Redirect to login page
        flash('You have been logged out.', 'info')
        return redirect(url_for('loginUser'))

    #ROUTE : DOCTOR MANAGEMENT

    @appObj.route('/admin/doctors')
    @adminRequired
    @login_required
    def listDoctors():
        # PROCESS: Query all Doctors (Role 2)
        doctorList = User.query.filter_by(role=ROLE_DOCTOR).all()
        # OUTPUT: Render list view
        return render_template('listDoctors.html', doctorList=doctorList)

    @appObj.route('/admin/doctors/add', methods=['GET', 'POST'])
    @adminRequired
    @login_required
    def addDoctor():
        if request.method == 'POST':
            # INPUT: Get form data
            userName = request.form.get('username')
            userPass = request.form.get('password')
            fullName = request.form.get('name')
            specialization = request.form.get('specialization')

            # PROCESS 1: Check for existing user
            if User.query.filter_by(username=userName).first():
                flash('Username already exists.', 'danger')
                return redirect(url_for('addDoctor'))

            # PROCESS 2: Hash password and save new Doctor (Role 2)
            passHashed = bCryptObj.generate_password_hash(userPass).decode('utf-8')

            newDoc = User(
                username=userName,
                password=passHashed,
                role=ROLE_DOCTOR,
                name=fullName,
                specialization=specialization,
                email=f"{userName}@doctor.com"
            )
            db.session.add(newDoc)
            db.session.commit()
            # OUTPUT: Redirect to list on success
            flash(f'Doctor {fullName} added successfully.', 'success')
            return redirect(url_for('listDoctors'))

        # OUTPUT: Render add form
        return render_template('addDoctor.html')

    @appObj.route('/admin/doctors/edit/<int:userID>', methods=['GET', 'POST'])
    @adminRequired
    @login_required
    def editDoctor(userID):
        # PROCESS 1: Get user to edit
        docUser = User.query.get_or_404(userID)

        # PROCESS 2: Security check (must be editing a Doctor)
        if docUser.role != ROLE_DOCTOR:
            flash('Error: Cannot edit this user role.', 'danger')
            return redirect(url_for('listDoctors'))

        if request.method == 'POST':
            # INPUT/PROCESS: Update details
            docUser.name = request.form.get('name')
            docUser.specialization = request.form.get('specialization')

            newPass = request.form.get('password')
            if newPass:
                docUser.password = bCryptObj.generate_password_hash(newPass).decode('utf-8')

            db.session.commit()
            # OUTPUT: Redirect to list on success
            flash(f'Doctor {docUser.name} updated successfully.', 'success')
            return redirect(url_for('listDoctors'))

        # OUTPUT: Render edit form
        return render_template('editDoctor.html', docUser=docUser)

    @appObj.route('/admin/users/delete/<int:userID>', methods=['POST'])
    @adminRequired
    @login_required
    def deleteUser(userID):
        # PROCESS 1: Get user to delete
        userToDelete = User.query.get_or_404(userID)

        # PROCESS 2: Security check (prevent deleting Admin)
        if userToDelete.role == ROLE_ADMIN:
            flash('Error: Cannot delete the Super Admin account.', 'danger')
            return redirect(url_for('listDoctors'))

        # PROCESS 3: Delete dependent Appointments (Data Integrity)
        Appointment.query.filter(
            or_(
                Appointment.doctor_id == userID,
                Appointment.patient_id == userID
            )
        ).delete()

        # PROCESS 4: Delete the user and commit
        db.session.delete(userToDelete)
        db.session.commit()

        # OUTPUT: Redirect to list on success
        flash(f'User "{userToDelete.name}" (ID: {userID}) has been deleted.', 'warning')
        return redirect(url_for('listDoctors'))

    #ROUTE : APPOINTMENT SYSTEM

    @appObj.route('/patient/appointments/book', methods=['GET', 'POST'])
    @login_required
    def bookAppointment():
        # PROCESS 1: RBAC check for patient role
        if current_user.role != ROLE_PATIENT:
            flash('Only patients can book appointments.', 'danger')
            return redirect(url_for('dashboardPage'))

        # PROCESS 2: Fetch available doctors for selection
        availableDoctors = User.query.filter_by(role=ROLE_DOCTOR).all()

        if request.method == 'POST':
            # INPUT: Get form data
            doctorID = request.form.get('doctorID')
            apptDate = request.form.get('date')
            apptTime = request.form.get('time')

            # PROCESS 3: Validation - check if date is in the past
            try:
                apptDateTime = datetime.datetime.strptime(
                    f"{apptDate} {apptTime}",
                    "%Y-%m-%d %H:%M"
                )
                if apptDateTime < datetime.datetime.now():
                    flash("Cannot book an appointment in the past.", 'danger')
                    return redirect(url_for('bookAppointment'))
            except ValueError:
                flash("Invalid date or time format.", 'danger')
                return redirect(url_for('bookAppointment'))

            # PROCESS 4: Prevent double booking for same doctor/date/time (except cancelled)
            clashing = Appointment.query.filter_by(
                doctor_id=doctorID,
                date=apptDate,
                time=apptTime
            ).filter(Appointment.status != 'Cancelled').first()

            if clashing:
                flash("This doctor already has an appointment at this time.", 'danger')
                return redirect(url_for('bookAppointment'))

            # PROCESS 5: Create and save the new appointment
            newAppt = Appointment(
                doctor_id=doctorID,
                patient_id=current_user.id,
                date=apptDate,
                time=apptTime,
                status='Booked'
            )

            db.session.add(newAppt)
            db.session.commit()
            # OUTPUT: Redirect to list view on success
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('listPatientAppointments'))

        # OUTPUT: Render booking form
        return render_template('bookAppo.html', doctorList=availableDoctors)

    @appObj.route('/patient/appointments')
    @login_required
    def listPatientAppointments():
        # PROCESS 1: Determine query based on user role
        if current_user.role == ROLE_PATIENT:
            # Patient: sees only their own appointments
            apptList = Appointment.query.filter_by(patient_id=current_user.id).all()
        elif current_user.role == ROLE_DOCTOR:
            # Doctor: sees appointments scheduled with them
            apptList = Appointment.query.filter_by(doctor_id=current_user.id).all()
        elif current_user.role == ROLE_ADMIN:
            # Admin: sees all appointments
            apptList = Appointment.query.all()
        else:
            flash("Access denied.", 'danger')
            return redirect(url_for('dashboardPage'))

        # OUTPUT: Render list view
        return render_template('listAppo.html', apptList=apptList)

    @appObj.route('/doctor/appointments/<int:apptID>', methods=['GET', 'POST'])
    @login_required
    def doctorUpdateAppointment(apptID):
        # PROCESS 1: Role check
        if current_user.role != ROLE_DOCTOR:
            flash("Only doctors can update appointments.", 'danger')
            return redirect(url_for('dashboardPage'))

        # PROCESS 2: Fetch appointment
        appt = Appointment.query.get_or_404(apptID)

        # PROCESS 3: Security - only assigned doctor
        if appt.doctor_id != current_user.id:
            flash("You are not assigned to this appointment.", 'danger')
            return redirect(url_for('listPatientAppointments'))

        if request.method == 'POST':
            # INPUT / PROCESS: Update status + treatment
            appt.status = request.form.get('status')
            appt.diagnosis = request.form.get('diagnosis')
            appt.prescription = request.form.get('prescription')

            db.session.commit()
            # OUTPUT: Redirect with success
            flash("Appointment updated successfully.", 'success')
            return redirect(url_for('listPatientAppointments'))

        # OUTPUT: Render doctor update form
        return render_template('docappo.html', appt=appt)

    @appObj.route('/appointments/cancel/<int:apptID>', methods=['POST'])
    @login_required
    def cancelAppointment(apptID):
        # PROCESS 1: Fetch appointment object
        appt = Appointment.query.get_or_404(apptID)

        # PROCESS 2: Authorization Check
        if current_user.role == ROLE_PATIENT and appt.patient_id != current_user.id:
            flash('You are not authorized to cancel this appointment.', 'danger')
        else:
            # PROCESS 3: Update status to 'Cancelled'
            appt.status = 'Cancelled'
            db.session.commit()
            flash(f'Appointment ID {apptID} has been cancelled.', 'warning')

        # OUTPUT: Redirect back to the appointment list
        return redirect(url_for('listPatientAppointments'))

    return appObj


#EXECUTION : START APP
if __name__ == '__main__':
    # PROCESS: Write dependencies list
    with open('requirements.txt', 'w') as fileReq:
        fileReq.write('Flask\nFlask-SQLAlchemy\nFlask-Login\nFlask-Bcrypt\n')

    app = createApp()
    app.run(debug=True)
