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

export function apiListDoctors() {
  return api.get("/api/doctors");
}

export function apiAdminAddDoctor(payload) {
  return api.post("/api/admin/doctors", payload);
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


