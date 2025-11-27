<script setup>
// SETUP: Imports
import { ref, onMounted } from "vue";
import {
  apiGetMe,
  apiDoctorListAppointments,
  apiDoctorUpdateAppointment,
} from "../api";

// INIT: State
const me = ref(null);
const appointments = ref([]);
const selected = ref(null);
const diagnosis = ref("");
const prescription = ref("");
const status = ref("Completed");
const error = ref("");
const message = ref("");

// PROCESS: Load profile + appointments
async function loadAppointments() {
  error.value = "";
  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;

    const resAppts = await apiDoctorListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    error.value = "Failed to load doctor data";
  }
}

// PROCESS: Select an appointment row
function selectAppointment(appt) {
  selected.value = appt;
  diagnosis.value = appt.diagnosis || "";
  prescription.value = appt.prescription || "";
  status.value = appt.status || "Completed";
  error.value = "";
  message.value = "";
}

// PROCESS: Save treatment for selected appointment
async function saveTreatment() {
  if (!selected.value) return;

  error.value = "";
  message.value = "";

  try {
    await apiDoctorUpdateAppointment(selected.value.id, {
      diagnosis: diagnosis.value,
      prescription: prescription.value,
      status: status.value,
    });

    message.value = "Treatment details saved";

    // reload list so UI is updated
    await loadAppointments();
  } catch (e) {
    error.value =
      e.response?.data?.error || "Failed to save treatment details";
  }
}

// INIT: On mount
onMounted(loadAppointments);
</script>

<template>
  <div>
    <h3 class="mb-3">Doctor Dashboard</h3>

    <p v-if="me">Welcome, Dr. {{ me.name }}</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row">
      <!-- LEFT: Appointment list -->
      <div class="col-md-7">
        <h5>My Appointments</h5>
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="appointments.length === 0">
              <td colspan="4" class="text-muted text-center">
                No appointments yet.
              </td>
            </tr>
            <tr
              v-for="appt in appointments"
              :key="appt.id"
              :class="{ 'table-active': selected && selected.id === appt.id }"
              @click="selectAppointment(appt)"
              style="cursor: pointer"
            >
              <td>{{ appt.date }}</td>
              <td>{{ appt.time }}</td>
              <td>{{ appt.patient_name || appt.patient_username }}</td>
              <td>
                <span
                  class="badge"
                  :class="{
                    'bg-secondary': appt.status === 'Booked',
                    'bg-success': appt.status === 'Completed',
                    'bg-danger': appt.status === 'Cancelled'
                  }"
                >
                  {{ appt.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- RIGHT: Treatment form -->
      <div class="col-md-5">
        <h5>Treatment Details</h5>

        <div v-if="!selected" class="text-muted">
          Select an appointment from the table to add diagnosis and prescription.
        </div>

        <div v-else>
          <p>
            <strong>Patient:</strong>
            {{ selected.patient_name || selected.patient_username }}<br />
            <strong>Time:</strong> {{ selected.date }} {{ selected.time }}
          </p>

          <form @submit.prevent="saveTreatment">
            <div class="mb-3">
              <label class="form-label">Diagnosis</label>
              <textarea
                v-model="diagnosis"
                class="form-control"
                rows="2"
                required
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea
                v-model="prescription"
                class="form-control"
                rows="2"
                required
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Status</label>
              <select v-model="status" class="form-select">
                <option value="Booked">Booked</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>

            <button class="btn btn-primary">
              Save Treatment
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
