# Medaleon Hospital Management System (MAD-2)

Medaleon HMS is my **Modern Application Development II** project, built as a full-stack hospital scheduling and treatment management platform.

It is the upgraded continuation of my MAD-1 system, redesigned with:
- a **Vue 3 SPA frontend**,  
- a **Flask REST backend**, and  
- role-specific dashboards for **Admin**, **Doctor**, and **Patient**.

The goal was to create a realistic clinic management workflow including appointment booking, treatment updates, role-based access, and an admin-level simulation runner.

## 1. Features at a Glance

### **Admin**
- Auto-created default admin (`admin / admin`) on first run :contentReference[oaicite:5]{index=5}  
- Manage doctors (add, edit, remove)  
- View:
  - All appointments (with doctor/patient names & status)
  - All registered patients
  - Summary metrics (counts of doctors, patients, bookings, etc.)  
- Run background **simulation task** (threaded)  
- Check simulation status (timestamped)  

### **Doctor**
- View **all appointments assigned to them**  
- Update:
  - Appointment status (Booked → Completed / Cancelled)
  - Diagnosis
  - Prescription  
- Patient name lookups included in appointment responses  

### **Patient**
- Register & login  
- Book appointments with:
  - Doctor selection
  - Date/time validation
  - Full conflict-prevention (prevents double-bookings)  
- Reschedule or cancel own appointments  
- View treatment details (diagnosis + prescription)

## 2. Tech Stack

### **Frontend (Vue 3 + Vite)**  
- Vue 3 (Composition API)  
- Vue Router with role-based navigation guards :contentReference[oaicite:6]{index=6}  
- Axios for API calls  
- Bootstrap 5  
- Custom splash screen, theme CSS, Medaleon branding  
- PWA basics (manifest + service worker)
- Fake background simulation

### **Backend (Flask REST API)**  
- Flask  
- Flask-SQLAlchemy (SQLite DB)  
- bcrypt password hashing  
- Custom JWT auth (`create_token`, `require_auth`)  
- Role decorators: `admin_required`, `doctor_required`, `patient_required`  
- Background simulation via Python threads  

## 3. Project Structure

project-root/
│
├── backend/
│   ├── app.py                 # Main Flask API (routes, auth, admin seed)  
│   ├── dba.py                 # DB models: User, Appointment, Treatment    
│   ├── authutils.py           # JWT + role-based access control
│   ├── api.yaml               # API spec (optional)
│   ├── instance/hms.db        # SQLite database
│   └── requirements.txt
│
├── frontend/hmsvue/
│   ├── public/                # Icons, manifest, serviceworker
│   ├── src/
│   │   ├── views/             # Admin, Doctor, Patient, Login, Register
│   │   ├── components/        # SplashScreen, OverviewCard
│   │   ├── api.js             # Axios API helpers                       
│   │   ├── router.js          # Route definitions + guards              
│   │   └── styles/            # theme.css, global UI styles
│   ├── package.json
│   └── vite.config.js
│
└── reports/
    ├── ER-diagram.png
    └── Screenshots/           # System screenshots

## 4. Authentication & Authorization

### JWT-based:
Every login returns:
```json
{ "token": "...", "role": "admin/doctor/patient" }
````
Stored in `localStorage` (Frontend) → automatically attached to Axios headers.
Protected routes on backend use:

* `@require_auth`
* `@admin_required`
* `@doctor_required`
* `@patient_required`

Browser routing is enforced by Vue Router:

```js
meta: { requiresAuth: true, role: "admin" }
```
## 5. API Overview (Based on Actual Backend)

### **Auth**

| Method | Endpoint        | Description                |
| ------ | --------------- | -------------------------- |
| POST   | `/api/register` | Patient registration       |
| POST   | `/api/login`    | Login → returns JWT + role |

### **Admin**

| Method | Endpoint                            | Purpose                       |
| ------ | ----------------------------------- | ----------------------------- |
| GET    | `/api/admin/summary`                | Metrics dashboard             |
| GET    | `/api/admin/appointments`           | All appointments              |
| GET    | `/api/admin/patients`               | All patients                  |
| GET    | `/api/admin/doctors`                | List doctors                  |
| POST   | `/api/admin/doctors`                | Add doctor                    |
| GET    | `/api/admin/run-simulation-task`    | Trigger background simulation |
| GET    | `/api/admin/simulation-task-status` | Check simulation status       |

### **Doctor**

| Method | Endpoint                        |
| ------ | ------------------------------- |
| GET    | `/api/doctor/appointments`      |
| PUT    | `/api/doctor/appointments/<id>` |

### **Patient**

| Method | Endpoint                         |
| ------ | -------------------------------- |
| POST   | `/api/patient/appointments`      |
| GET    | `/api/patient/appointments`      |
| PUT    | `/api/patient/appointments/<id>` |

## 6. Frontend Screens

### Built from vue files

* `AdminDashboard.vue`
* `DoctorDashboard.vue`
* `PatientDashboard.vue`
* `LoginView.vue`
* `RegisterView.vue`

The system includes:

* 2-second animated splash screen
* Navigation bar with dynamic role buttons
* Appointment tables
* Status filters
* Doctor add/edit/remove modals
* Patient booking UI
* Doctor treatment update UI

## 🛠 7. How to Run (Backend)

```bash
cd backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
python app.py
```

Backend runs at: http://localhost:5000

Admin auto-created on first seed run:
**username:** admin
**password:** admin 

---

## 8. How to Run (Frontend)

```bash
cd frontend/hmsvue
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

## 9. Testing Checklist

* Login as patient → book appointment → reschedule → cancel
* Login as doctor → complete appointment → add diagnosis/prescription
* Login as admin → verify summary counts
* Admin → add doctor → edit doctor → remove doctor
* Admin → run simulation → check status
* Refresh browser: role stays synced due to localStorage
* Double-booking prevented (backend validated)
* Invalid doctor IDs blocked
* Auth guard correctly redirects unauthorized roles

## 10. Notes

* SQLite DB auto-created on first run
* Simulation uses Python threads (non-blocking)
* Appointment conflicts prevented at backend level
* Roles fully isolated (Admin cannot access doctor endpoints, etc.)

## 11. Conclusion

This project delivers a complete hospital workflow:

* registration,
* booking,
* treatment,
* role-specific dashboards,
* and admin-level management tools.
