<script setup>
// SETUP: Imports
import { ref, computed, onMounted } from "vue";
import {
  apiGetMe,
  apiAdminAddDoctor,
  apiAdminListDoctors,
  apiAdminSummary,
  apiAdminListAppointments,
  apiAdminRunSimulationTask,
  apiAdminSimulationStatus,
} from "../api";

// STATE: user + messages
const me = ref(null);
const message = ref("");
const error = ref("");

// STATE: summary counters
const summary = ref(null);

// STATE: doctors
const doctors = ref([]);
const doctorForm = ref({
  username: "",
  name: "",
  email: "",
  specialization: "",
  password: "",
});

// STATE: appointments (admin view)
const appointments = ref([]);
const apptLoading = ref(false);
const apptError = ref("");

// filters for appointments
const apptSearch = ref("");
const apptStatusFilter = ref(""); // "", "Booked", "Completed", "Cancelled"

// STATE: background simulation
const simMessage = ref("");
const simDetails = ref("");
const simLastRun = ref(null);

// LOAD: initial data
async function loadAdminData() {
  message.value = "";
  error.value = "";
  apptError.value = "";

  try {
    const resMe = await apiGetMe();
    me.value = resMe.data;
  } catch (e) {
    console.error("Error loading /api/me", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load profile (${e.response?.status || "no status"})`;
    return;
  }

  try {
    const [resSummary, resDoctors, resAppts] = await Promise.all([
      apiAdminSummary(),
      apiAdminListDoctors(),
      apiAdminListAppointments(),
    ]);

    summary.value = resSummary.data;
    doctors.value = resDoctors.data;
    appointments.value = resAppts.data;
  } catch (e) {
    console.error("Error loading admin data", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load admin data (${e.response?.status || "no status"})`;
  }
}

// ACTION: add doctor
async function addDoctor() {
  message.value = "";
  error.value = "";

  try {
    await apiAdminAddDoctor(doctorForm.value);
    message.value = "Doctor added";

    // refresh doctor list
    const resDocs = await apiAdminListDoctors();
    doctors.value = resDocs.data;

    // reset form
    doctorForm.value = {
      username: "",
      name: "",
      email: "",
      specialization: "",
      password: "",
    };
  } catch (e) {
    console.error("Error adding doctor", e);
    error.value = e.response?.data?.error || "Failed to add doctor";
  }
}

// COMPUTED: filtered appointments
const filteredAppointments = computed(() => {
  const term = apptSearch.value.trim().toLowerCase();
  const status = apptStatusFilter.value;

  return appointments.value.filter((a) => {
    const matchesStatus = !status || a.status === status;

    const combined =
      `${a.date} ${a.time} ${a.doctor_name || ""} ${a.doctor_username || ""} ` +
      `${a.patient_name || ""} ${a.patient_username || ""}`.toLowerCase();

    const matchesSearch = !term || combined.includes(term);

    return matchesStatus && matchesSearch;
  });
});

// ACTION: manual refresh for appointments
async function refreshAppointments() {
  apptLoading.value = true;
  apptError.value = "";
  try {
    const res = await apiAdminListAppointments();
    appointments.value = res.data;
  } catch (e) {
    console.error("Error loading appointments", e);
    apptError.value =
      e.response?.data?.error || "Failed to load appointments";
  } finally {
    apptLoading.value = false;
  }
}

// ACTION: run simulation task
async function runSimulation() {
  simMessage.value = "";
  simDetails.value = "";
  error.value = "";

  try {
    const res = await apiAdminRunSimulationTask();
    simMessage.value = res.data?.message || "Simulation started";
    simDetails.value =
      res.data?.details ||
      "A background simulation task is now running.";
    simLastRun.value = new Date().toLocaleTimeString();
  } catch (e) {
    console.error("Error starting simulation", e);
    error.value =
      e.response?.data?.error || "Failed to start simulation task.";
  }
}

// ACTION: check simulation status
async function checkSimulationStatus() {
  simMessage.value = "";
  simDetails.value = "";
  error.value = "";

  try {
    const res = await apiAdminSimulationStatus();
    simMessage.value = res.data?.status || "Status fetched";
    simDetails.value =
      res.data?.note || "Background simulation status updated.";
  } catch (e) {
    console.error("Error checking simulation status", e);
    error.value =
      e.response?.data?.error || "Failed to check simulation status.";
  }
}

onMounted(loadAdminData);
</script>

<template>
  <div>
    <h3 class="mb-3">Admin Dashboard</h3>

    <p v-if="me">Logged in as {{ me.name }} ({{ me.role }})</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- SUMMARY CARDS -->
    <div v-if="summary" class="row mb-4">
      <div class="col-md-3 mb-2">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h6 class="card-title text-muted">Doctors</h6>
            <p class="display-6 mb-0">{{ summary.total_doctors }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-2">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h6 class="card-title text-muted">Patients</h6>
            <p class="display-6 mb-0">{{ summary.total_patients }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-2">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h6 class="card-title text-muted">Appointments</h6>
            <p class="display-6 mb-1">{{ summary.total_appointments }}</p>
            <small class="text-muted">
              {{ summary.booked }} booked ·
              {{ summary.completed }} completed ·
              {{ summary.cancelled }} cancelled
            </small>
          </div>
        </div>
      </div>

      <!-- Background Simulation panel -->
      <div class="col-md-3 mb-2">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h6 class="card-title">Background Simulation</h6>
            <p class="small text-muted mb-2">
              Demonstrates running a simulated background task (for example,
              generating a system report) without blocking the interface.
            </p>
            <div class="d-flex gap-2 mb-2">
              <button class="btn btn-sm btn-primary" @click="runSimulation">
                Run Simulation Task
              </button>
              <button class="btn btn-sm btn-outline-secondary" @click="checkSimulationStatus">
                Check Status
              </button>
            </div>
            <div v-if="simMessage" class="small">
              <strong>Message:</strong> {{ simMessage }}<br />
              <span v-if="simDetails"><strong>Details:</strong> {{ simDetails }}</span>
              <br v-if="simLastRun" />
              <span v-if="simLastRun" class="text-muted">
                Last started at {{ simLastRun }}
              </span>
            </div>
            <div v-else class="small text-muted">
              No simulation has been run yet in this session.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DOCTOR MANAGEMENT + APPOINTMENTS -->
    <div class="row">
      <!-- LEFT: Add Doctor + Doctors list -->
      <div class="col-lg-5 mb-4">
        <div class="card shadow-sm mb-3">
          <div class="card-body">
            <h5 class="card-title">Add Doctor</h5>
            <form @submit.prevent="addDoctor">
              <div class="mb-2">
                <label class="form-label">Username</label>
                <input v-model="doctorForm.username" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Name</label>
                <input v-model="doctorForm.name" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Email</label>
                <input
                  v-model="doctorForm.email"
                  type="email"
                  class="form-control"
                  required
                />
              </div>
              <div class="mb-2">
                <label class="form-label">Specialization</label>
                <input v-model="doctorForm.specialization" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input
                  v-model="doctorForm.password"
                  type="password"
                  class="form-control"
                  required
                />
              </div>
              <button class="btn btn-primary">Save</button>
            </form>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Doctors</h5>
            <table class="table table-sm mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>User</th>
                  <th>Email</th>
                  <th>Spec</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in doctors" :key="d.id">
                  <td>{{ d.name }}</td>
                  <td>{{ d.username }}</td>
                  <td>{{ d.email }}</td>
                  <td>{{ d.specialization || "-" }}</td>
                </tr>
                <tr v-if="doctors.length === 0">
                  <td colspan="4" class="text-muted text-center small">
                    No doctors added yet.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- RIGHT: All Appointments -->
      <div class="col-lg-7 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="card-title mb-0">All Appointments</h5>
              <button class="btn btn-sm btn-outline-secondary" @click="refreshAppointments">
                Refresh
              </button>
            </div>

            <!-- Filters -->
            <div class="row g-2 mb-3">
              <div class="col-md-8">
                <input
                  v-model="apptSearch"
                  class="form-control form-control-sm"
                  placeholder="Search by patient, doctor, date or time..."
                />
              </div>
              <div class="col-md-4">
                <select
                  v-model="apptStatusFilter"
                  class="form-select form-select-sm"
                >
                  <option value="">All statuses</option>
                  <option value="Booked">Booked</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            <div v-if="apptError" class="alert alert-danger py-2">
              {{ apptError }}
            </div>

            <div class="table-responsive flex-grow-1">
              <table class="table table-sm table-striped mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Doctor</th>
                    <th>Patient</th>
                    <th>Status</th>
                    <th>Diagnosis</th>
                    <th>Prescription</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="apptLoading">
                    <td colspan="7" class="text-center text-muted">
                      Loading appointments…
                    </td>
                  </tr>
                  <tr v-else-if="filteredAppointments.length === 0">
                    <td colspan="7" class="text-center text-muted">
                      No appointments match the current filters.
                    </td>
                  </tr>
                  <tr
                    v-for="a in filteredAppointments"
                    :key="a.id"
                  >
                    <td>{{ a.date }}</td>
                    <td>{{ a.time }}</td>
                    <td>
                      {{ a.doctor_name || a.doctor_username || "-" }}
                    </td>
                    <td>
                      {{ a.patient_name || a.patient_username || "-" }}
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="{
                          'bg-secondary': a.status === 'Booked',
                          'bg-success': a.status === 'Completed',
                          'bg-danger': a.status === 'Cancelled'
                        }"
                      >
                        {{ a.status }}
                      </span>
                    </td>
                    <td>{{ a.diagnosis || "-" }}</td>
                    <td>{{ a.prescription || "-" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>
