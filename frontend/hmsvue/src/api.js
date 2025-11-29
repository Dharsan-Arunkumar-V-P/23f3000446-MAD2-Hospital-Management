// SETUP: Imports
import axios from "axios";

// INIT: Axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000",
});

// PROCESS: Attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// OUTPUT: API helpers
export function apiLogin(username, password) {
  return api.post("/api/login", { username, password });
}

export function apiRegister(payload) {
  return api.post("/api/register", payload);
}

export function apiGetMe() {
  return api.get("/api/me");
}

//INIT: Admin Controls
export function apiAdminListDoctors() {
  return api.get("/api/admin/doctors");
}

export function apiAdminSummary() {
  return api.get("/api/admin/summary");
}

export function apiAdminListPatients() {
  return api.get("/api/admin/patients");
}

export function apiAdminListAppointments() {
  return api.get("/api/admin/appointments");
}

export function apiListDoctors() {
  return api.get("/api/doctors");
}

export function apiAdminAddDoctor(payload) {
  return api.post("/api/admin/doctors", payload);
}

export function apiAdminTriggerReminders() {
  return api.post("/api/admin/tasks/reminders");
}

export function apiAdminTriggerExportAppointments() {
  return api.post("/api/admin/tasks/export-appointments");
}

export function apiAdminTaskStatus(taskId) {
  return api.get(`/api/admin/tasks/${taskId}`);
}

export async function apiAdminUpdateDoctor(id, payload) {
  console.info("[api] UPDATE doctor", id, payload);
  try {
    const res = await api.put(`/api/admin/doctors/${id}`, payload);
    console.info("[api] UPDATE res", res.status, res.data);
    return res;
  } catch (err) {
    console.error("[api] UPDATE error", err.response?.status, err.response?.data || err.message);
    throw err;
  }
}

export async function apiAdminRemoveDoctor(id) {
  console.info("[api] REMOVE doctor", id);
  try {
    const res = await api.delete(`/api/admin/doctors/${id}`);
    console.info("[api] REMOVE res", res.status, res.data);
    return res;
  } catch (err) {
    console.error("[api] REMOVE error", err.response?.status, err.response?.data || err.message);
    throw err;
  }
}

//INIT: Doc & Appt
export function apiDoctorUpdateAppointment(id, payload) {
  return api.put(`/api/doctor/appointments/${id}`, payload);
}

export function apiDoctorListAppointments() {
  return api.get("/api/doctor/appointments");
}


//INIT: Pat & Appt
export function apiPatientBookAppointment(payload) {
  return api.post("/api/patient/appointments", payload);
}

export function apiPatientListAppointments() {
  return api.get("/api/patient/appointments");
}

export function apiPatientUpdateAppointment(id, payload) {
  return api.put(`/api/patient/appointments/${id}`, payload);
}

//INIT: Simulation
export function apiAdminRunSimulationTask() {
  return api.get("/api/admin/run-simulation-task");
}

export function apiAdminSimulationStatus() {
  return api.get("/api/admin/simulation-task-status");
}
