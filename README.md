# MAD-1 Hospital Management System (HMS)

A simple Hospital Management System built as part of the IITM BS Degree **MAD-1** project.

The application supports three roles:

- **Admin** – manages doctors and can view all appointments.
- **Doctor** – views their assigned appointments and records treatments.
- **Patient** – registers, books appointments, cancels them, and views history

## 1. Tech Stack

- Python 3 + **Flask**
- **Flask-SQLAlchemy** (ORM, SQLite backend)
- **Flask-Login** (authentication & session management)
- **Flask-Bcrypt** (password hashing)
- **Jinja2** templates
- **Bootstrap 5** for styling

## 2. Features

### Admin
- Auto-created **Super Admin** user  
  - Username: `admin`  
  - Password: `admin_pass`
- Admin dashboard:  
  - Total Doctors  
  - Total Patients  
  - Total Appointments
- Manage Doctors (CRUD):
  - Add doctor with specialization
  - Edit doctor details and password
  - Delete doctor (and their appointments)
- View all appointments in the system

### Doctor
- Doctor dashboard with quick links
- View all appointments assigned to the doctor
- For each appointment:
  - Update **status**: Booked / Completed / Cancelled
  - Add **diagnosis**
  - Add **prescription**
- Changes are reflected in both doctor and patient views as treatment history

### Patient
- Register as a new patient
- Login and view **Patient Panel**
- See available **departments/specializations** derived from doctor specializations
- Book appointment with any doctor:
  - Date & time must be in the future
  - Prevents double-booking (same doctor, same date, same time)
- Cancel booked appointments
- View full appointment history including diagnosis & prescription


## 3. Project Structure

```text
project-root/
│ app.py                  # Main Flask application (routes, auth, dashboards)
│ dba.py                  # SQLAlchemy models: User, Appointment
│ requirements.txt        # Dependencies
│ api.yaml                # OpenAPI specification (documentation)
│
├─templates/
│   base.html
│   login.html
│   register.html
│   dashboard.html
│   listDoctors.html
│   addDoctor.html
│   editDoctor.html
│   bookAppo.html
│   listAppo.html
│   docappo.html
│
└─static/
    styles.css            # Optional custom CSS
