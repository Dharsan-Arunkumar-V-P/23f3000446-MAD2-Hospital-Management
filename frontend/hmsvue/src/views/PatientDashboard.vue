<script setup>
import { ref, onMounted } from "vue";
import {
  apiGetMe,
  apiAdminSummary,
  apiAdminListDoctors,
  apiAdminListPatients,
  apiAdminListAppointments,
  apiAdminAddDoctor,
} from "../api";

const me = ref(null);

const summary = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  booked: 0,
  completed: 0,
  cancelled: 0,
});

const doctors = ref([]);
const patients = ref([]);
const appointments = ref([]);

const message = ref("");
const error = ref("");
const loading = ref(false);

// add-doctor form
const docForm = ref({
  username: "",
  name: "",
  email: "",
  specialization: "",
  password: "",
});

// LOAD: admin profile + summary + doctors + patients + appointments
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
    const resSummary = await apiAdminSummary();
    summary.value = resSummary.data;
  } catch (e) {
    console.error("Error loading /api/admin/summary", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load summary (${e.response?.status || "no status"})`;
  }

  try {
    const resDoctors = await apiAdminListDoctors();
    doctors.value = resDoctors.data;
  } catch (e) {
    console.error("Error loading /api/admin/doctors", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load doctors (${e.response?.status || "no status"})`;
  }

  try {
    const resPatients = await apiAdminListPatients();
    patients.value = resPatients.data;
  } catch (e) {
    console.error("Error loading /api/admin/patients", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load patients (${e.response?.status || "no status"})`;
  }

  try {
    const resAppts = await apiAdminListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    console.error("Error loading /api/admin/appointments", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load appointments (${e.response?.status || "no status"})`;
  } finally {
    loading.value = false;
  }
}

// ADD DOCTOR
async function addDoctor() {
  error.value = "";
  message.value = "";

  if (!docForm.value.username || !docForm.value.password) {
    error.value = "Username and password are required.";
    return;
  }

  try {
    const res = await apiAdminAddDoctor(docForm.value);
    doctors.value.push(res.data);
    message.value = "Doctor added successfully.";

    docForm.value = {
      username: "",
      name: "",
      email: "",
      specialization: "",
      password: "",
    };
  } catch (e) {
    console.error("Error adding doctor", e);
    error.value =
      e.response?.data?.error || "Failed to add doctor. Please try again.";
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Admin Dashboard</h3>

    <p v-if="me">Welcome, {{ me.name }} (Admin)</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div
      v-if="loading"
      class="alert alert-info py-2"
    >
      Loading data...
    </div>

    <!-- SUMMARY CARDS -->
    <div class="row mb-4">
      <div class="col-md-3 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <div class="fw-bold">Doctors</div>
            <div class="fs-4">{{ summary.total_doctors }}</div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <div class="fw-bold">Patients</div>
            <div class="fs-4">{{ summary.total_patients }}</div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <div class="fw-bold">Appointments</div>
            <div class="fs-4">{{ summary.total_appointments }}</div>
            <small class="text-muted">
              Booked: {{ summary.booked }},
              Completed: {{ summary.completed }},
              Cancelled: {{ summary.cancelled }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- LEFT: Doctors + Add Doctor -->
      <div class="col-md-5">
        <h5>Doctors</h5>
        <table class="table table-striped table-sm align-middle">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>Specialization</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="doctors.length === 0">
              <td colspan="4" class="text-muted text-center">
                No doctors added yet.
              </td>
            </tr>
            <tr
              v-for="d in doctors"
              :key="d.id"
            >
              <td>{{ d.username }}</td>
              <td>{{ d.name }}</td>
              <td>{{ d.email }}</td>
              <td>{{ d.specialization || "-" }}</td>
            </tr>
          </tbody>
        </table>

        <h6 class="mt-3">Add Doctor</h6>
        <form @submit.prevent="addDoctor">
          <div class="mb-2">
            <label class="form-label">Username</label>
            <input
              v-model="docForm.username"
              type="text"
              class="form-control"
              required
            />
          </div>
          <div class="mb-2">
            <label class="form-label">Name</label>
            <input
              v-model="docForm.name"
              type="text"
              class="form-control"
            />
          </div>
          <div class="mb-2">
            <label class="form-label">Email</label>
            <input
              v-model="docForm.email"
              type="email"
              class="form-control"
            />
          </div>
          <div class="mb-2">
            <label class="form-label">Specialization</label>
            <input
              v-model="docForm.specialization"
              type="text"
              class="form-control"
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="docForm.password"
              type="password"
              class="form-control"
              required
            />
          </div>
          <button class="btn btn-primary btn-sm">Add Doctor</button>
        </form>
      </div>

      <!-- RIGHT: Patients + Appointments -->
      <div class="col-md-7">
        <h5>Patients</h5>
        <table class="table table-striped table-sm align-middle">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="patients.length === 0">
              <td colspan="3" class="text-muted text-center">
                No patients registered yet.
              </td>
            </tr>
            <tr
              v-for="p in patients"
              :key="p.id"
            >
              <td>{{ p.username }}</td>
              <td>{{ p.name }}</td>
              <td>{{ p.email }}</td>
            </tr>
          </tbody>
        </table>

        <h5 class="mt-4">All Appointments</h5>
        <table class="table table-striped table-sm align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Patient</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="appointments.length === 0">
              <td colspan="5" class="text-muted text-center">
                No appointments yet.
              </td>
            </tr>
            <tr
              v-for="a in appointments"
              :key="a.id"
            >
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>{{ a.doctor_name || a.doctor_username }}</td>
              <td>{{ a.patient_name || a.patient_username }}</td>
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
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
