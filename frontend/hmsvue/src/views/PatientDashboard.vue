<script setup>
// SETUP: Imports
import { ref, onMounted } from "vue";
import {
  apiGetMe,
  apiPatientBookAppointment,
  apiPatientListAppointments,
  apiListDoctors,
} from "../api";

// INIT: State
const me = ref(null);
const doctors = ref([]);
const appointments = ref([]);
const message = ref("");
const error = ref("");

const form = ref({
  doctor_id: "",
  date: "",
  time: "",
});

// PROCESS: Load profile, doctors, and appointments
async function load() {
  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;

    const resDocs = await apiListDoctors();
    doctors.value = resDocs.data;

    const resAppts = await apiPatientListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    error.value = "Failed to load patient data";
  }
}

// PROCESS: Book appointment
async function book() {
  error.value = "";
  message.value = "";

  try {
    await apiPatientBookAppointment(form.value);
    message.value = "Appointment booked";

    form.value = {
      doctor_id: "",
      date: "",
      time: "",
    };

    const resAppts = await apiPatientListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    error.value = e.response?.data?.error || "Failed to book appointment";
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Patient Dashboard</h3>

    <p v-if="me">Welcome, {{ me.name }}</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row">
      <!--LEFT: Book appointment-->
      <div class="col-md-5">
        <h5>Book Appointment</h5>
        <form @submit.prevent="book">
          <div class="mb-2">
            <label class="form-label">Doctor</label>
            <select
              v-model="form.doctor_id"
              class="form-select"
              required
            >
              <option value="" disabled>Select doctor</option>
              <option
                v-for="d in doctors"
                :key="d.id"
                :value="d.id"
              >
                {{ d.name }} ({{ d.specialization || 'General' }})
              </option>
            </select>
          </div>

          <div class="mb-2">
            <label class="form-label">Date</label>
            <input
              v-model="form.date"
              type="date"
              class="form-control"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Time</label>
            <input
              v-model="form.time"
              type="time"
              class="form-control"
              required
            />
          </div>

          <button class="btn btn-primary">Book</button>
        </form>
      </div>

      <!--RIGHT: Appointment list-->
      <div class="col-md-7">
        <h5>My Appointments</h5>
        <table class="table table-sm align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>{{ a.doctor_name || '-' }}</td>
              <td>{{ a.status }}</td>
            </tr>
            <tr v-if="appointments.length === 0">
              <td colspan="4" class="text-muted">No appointments yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
