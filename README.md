# MAD-2 Hospital Management System V2 (HMS-V2)

Hospital Management System V2 is the **MAD-2 upgrade** of my MAD-1 project.

- Backend: **Flask** REST API with SQLite, Redis cache, and Celery background jobs  
- Frontend: **VueJS** SPA consuming the Flask API  
- Roles: **Admin, Doctor, Patient**

Admins manage doctors and monitor the system, doctors handle treatments, and patients book / cancel appointments and view their medical history.

## 1. Tech Stack

### Backend (API)
- Python 3
- **Flask** – web framework / routing
- **Flask-SQLAlchemy** – ORM on **SQLite**
- **Flask-Login** – session & authentication
- **Flask-Bcrypt** – password hashing
- **Flask-CORS** – allow VueJS frontend to call the API
- **Redis** – caching (frequently used lists such as doctors, departments)
- **Celery** – background jobs (reminders, report generation)
- **OpenAPI (YAML)** – API documentation (`api.yaml`)

### Frontend (UI)
- **VueJS 3** (via Vue CLI or Vite)
- **Axios** for HTTP calls to Flask API
- **Bootstrap 5** for styling
- **Chart.js** (via `vue-chartjs`) for analytics charts

## 2. Core Features (MAD-2)

### Admin
- Auto-created **Super Admin**
  - Username: `admin`
  - Password: `admin`
- Dashboard:
  - Total doctors, patients, appointments (fetched via API)
  - Charts: appointment trends per day / specialization
- Manage Doctors:
  - Create doctor accounts with specialization & availability
  - Edit / deactivate doctor profiles
- View all appointments and treatments

### Doctor
- View upcoming appointments
- Update appointment **status** (Booked / Completed / Cancelled)
- Record **diagnosis**, **prescription**, and notes (Treatment)
- See patient history for their own patients

### Patient
- Register and login
- View list of departments and available doctors
- Book appointments with date/time validation + double-booking checks
- Cancel appointments
- View treatment history (diagnosis + prescription)

### System-level
- **Redis caching** for read-heavy data (doctor list, department list, dashboard metrics)
- **Celery tasks** for:
  - Sending reminder emails / console logs for appointments
  - Generating monthly summary reports (stored as PDF/JSON)
- **OpenAPI spec** (`api.yaml`) describing all important endpoints


## 3. Project Structure

project-root/
│
├── app.py               # Flask app + API routes
├── dba.py               # SQLAlchemy models (User, Doctor, Patient, Department, Appointment, Treatment)
├── authutils.py         # Role-based decorators
├── api.yaml             # OpenAPI 3 specification
├── requirements.txt     # Python dependencies
├── ER-diagram.png       # ER diagram for MAD-2 schema
├── README.md            # This file
│
├── instance/
│   └── hms.db           # SQLite DB (auto-created)
│
├── static/              # (optional) backend-only static assets
│
├── templates/           # Only minimal entry HTML if needed
│   └── index.html       # Optional initial mount point for Vue (or simple landing page)
│
└── frontend/            # VueJS SPA
    ├── package.json
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── api/        # Axios helpers
    │   ├── views/      # Login, Dashboard, DoctorView, PatientView
    │   └── components/
    └── public/

4. How to Run (Backend)

# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Initialize database (creates admin user)
flask --app app.py init-db

# 4. Run Flask API
flask --app app.py run
# API base URL: http://localhost:5000/api

5. How to Run (Frontend – VueJS)
cd frontend
npm install
npm run dev   # or npm run serve, depending on setup
# Frontend URL: http://localhost:5173 or http://localhost:8080

6. OpenAPI Specification

The file api.yaml documents the:
Auth endpoints (/api/auth/login, /api/auth/register)
Doctor management (/api/doctors/...)
Patient booking (/api/appointments/...)
Analytics endpoints for charts