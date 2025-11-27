// SETUP: Imports
import axios from "axios";

// INIT: Axios instance
const api = axios.create({
  baseURL: "http://localhost:5000",
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

export function apiPatientBookAppointment(payload) {
  return api.post("/api/patient/appointments", payload);
}

export function apiDoctorUpdateAppointment(id, payload) {
  return api.put(`/api/doctor/appointments/${id}`, payload);
}

export function apiDoctorListAppointments() {
  return api.get("/api/doctor/appointments");
}

export function apiPatientListAppointments() {
  return api.get("/api/patient/appointments");
}

export function apiPatientUpdateAppointment(id, payload) {
  return api.put(`/api/patient/appointments/${id}`, payload);
}



