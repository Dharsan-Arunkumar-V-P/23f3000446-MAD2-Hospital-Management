<script setup>
// SETUP: Imports
import { ref, onMounted } from "vue";
import { apiGetMe, apiDoctorListAppointments, apiDoctorUpdateAppointment } from "../api";

// INIT: State
const me = ref(null);
const appointments = ref([]);
const selected = ref(null);
const message = ref("");
const error = ref("");

const treatmentForm = ref({
  diagnosis: "",
  prescription: "",
  notes: "",
});

// PROCESS: Load profile + appointments
async function load() {
  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;

    const resAppts = await apiDoctorListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    error.value = "Failed to load doctor data";
  }
}

// PROCESS: Select appointment row
function selectAppointment(appt) {
  selected.value = appt;
  message.value = "";
  error.value = "";
  treatmentForm.value = {
    diagnosis: "",
    prescription: "",
    notes: "",
  };
}

// PROCESS: Save treatment for selected appointment
async function saveTreatment() {
  if (!selected.value) return;

  message.value = "";
  error.value = "";

  try {
    await apiDoctorUpdateAppointment(selected.value.id, treatmentForm.value);
    message.value = "Treatment details saved";
  } catch (e) {
    error.value = e.response?.data?.error || "Failed to save treatment";
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Doctor Dashboard</h3>

    <p v-if="me">Welcome, Dr. {{ me.name }}</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row">
      <!--LEFT: Appointment list-->
      <div class="col-md-7">
        <h5>My Appointments</h5>
        <table class="table table-hover table-sm align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="a in appointments"
              :key="a.id"
              :class="{ 'table-active': selected && selected.id === a.id }"
              style="cursor: pointer"
              @click="selectAppointment(a)"
            >
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>{{ a.patient_name || '-' }}</td>
              <td>{{ a.status }}</td>
            </tr>
            <tr v-if="appointments.length === 0">
              <td colspan="4" class="text-muted">No appointments yet.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!--RIGHT: Treatment form-->
      <div class="col-md-5">
        <h5>Treatment Details</h5>
        <p v-if="!selected" class="text-muted">
          Select an appointment from the table to add diagnosis and prescription.
        </p>

        <div v-else>
          <p>
            <strong>Patient:</strong> {{ selected.patient_name || '-' }}<br />
            <strong>Date:</strong> {{ selected.date }} {{ selected.time }}
          </p>

          <form @submit.prevent="saveTreatment">
            <div class="mb-2">
              <label class="form-label">Diagnosis</label>
              <textarea
                v-model="treatmentForm.diagnosis"
                class="form-control"
                rows="2"
              ></textarea>
            </div>
            <div class="mb-2">
              <label class="form-label">Prescription</label>
              <textarea
                v-model="treatmentForm.prescription"
                class="form-control"
                rows="2"
              ></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea
                v-model="treatmentForm.notes"
                class="form-control"
                rows="2"
              ></textarea>
            </div>

            <button class="btn btn-primary" :disabled="!treatmentForm.diagnosis && !treatmentForm.prescription">
              Save Treatment
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
