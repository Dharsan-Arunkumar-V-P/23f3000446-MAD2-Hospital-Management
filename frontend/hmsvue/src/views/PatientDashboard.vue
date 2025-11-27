<script setup>
import { ref, onMounted } from "vue";
import {
  apiGetMe,
  apiDoctorListAppointments,
  apiDoctorUpdateAppointment,
} from "../api";

const me = ref(null);
const appointments = ref([]);
const selected = ref(null);

const message = ref("");
const error = ref("");
const loading = ref(false);

// form for diagnosis/prescription/status editing
const form = ref({
  diagnosis: "",
  prescription: "",
  status: "Completed",
});

// load doctor profile + appointments
async function load() {
  error.value = "";
  message.value = "";
  loading.value = true;

  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;
  } catch (e) {
    console.error("Error loading /api/me", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load profile (${e.response?.status || "no status"})`;
    loading.value = false;
    return;
  }

  try {
    const resAppts = await apiDoctorListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    console.error("Error loading /api/doctor/appointments", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load appointments (${e.response?.status || "no status"})`;
  } finally {
    loading.value = false;
  }
}

// when clicking "Update" on a row
function selectAppointment(appt) {
  selected.value = appt;
  form.value = {
    diagnosis: appt.diagnosis || "",
    prescription: appt.prescription || "",
    status: appt.status || "Completed",
  };
  message.value = "";
  error.value = "";
}

// clear selection
function clearSelection() {
  selected.value = null;
  form.value = {
    diagnosis: "",
    prescription: "",
    status: "Completed",
  };
}

// save changes
async function save() {
  if (!selected.value) return;

  error.value = "";
  message.value = "";
  const id = selected.value.id;

  try {
    await apiDoctorUpdateAppointment(id, {
      diagnosis: form.value.diagnosis,
      prescription: form.value.prescription,
      status: form.value.status,
    });

    message.value = "Appointment updated";

    // reload appointments
    const resAppts = await apiDoctorListAppointments();
    appointments.value = resAppts.data;

    // keep selection in sync with new data
    const updated = appointments.value.find((a) => a.id === id);
    if (updated) {
      selected.value = updated;
    } else {
      clearSelection();
    }
  } catch (e) {
    console.error("Error updating appointment", e);
    const backendMsg = e.response?.data?.error || "";
    if (backendMsg) {
      error.value = backendMsg;
    } else {
      error.value = "Failed to update appointment. Please try again.";
    }
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

    <div v-if="loading" class="alert alert-info py-2">
      Loading your appointments...
    </div>

    <div class="row">
      <!-- LEFT: list of appointments -->
      <div class="col-md-7">
        <h5>My Appointments</h5>
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th>Status</th>
              <th style="width: 120px">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="appointments.length === 0">
              <td colspan="5" class="text-muted text-center">
                No appointments assigned.
              </td>
            </tr>
            <tr
              v-for="appt in appointments"
              :key="appt.id"
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
              <td>
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="selectAppointment(appt)"
                >
                  Update
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- RIGHT: selected appointment details / form -->
      <div class="col-md-5">
        <h5>Appointment Details</h5>

        <div v-if="!selected" class="text-muted">
          Select an appointment to view and update diagnosis / prescription.
        </div>

        <div v-else class="card">
          <div class="card-body">
            <p class="mb-1">
              <strong>Patient:</strong>
              {{ selected.patient_name || selected.patient_username }}
            </p>
            <p class="mb-1">
              <strong>Date:</strong> {{ selected.date }}
            </p>
            <p class="mb-1">
              <strong>Time:</strong> {{ selected.time }}
            </p>

            <hr />

            <div class="mb-2">
              <label class="form-label">Status</label>
              <select
                v-model="form.status"
                class="form-select"
              >
                <option value="Booked">Booked</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>

            <div class="mb-2">
              <label class="form-label">Diagnosis</label>
              <textarea
                v-model="form.diagnosis"
                class="form-control"
                rows="2"
                placeholder="Enter diagnosis notes"
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea
                v-model="form.prescription"
                class="form-control"
                rows="2"
                placeholder="Enter prescription details"
              ></textarea>
            </div>

            <div class="d-flex justify-content-between">
              <button
                type="button"
                class="btn btn-secondary"
                @click="clearSelection"
              >
                Clear
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="save"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
