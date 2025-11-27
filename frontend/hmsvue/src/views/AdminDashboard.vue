//SETUP: Imports
<script setup>
import { ref, onMounted } from "vue";
import {
  apiGetMe,
  apiAdminAddDoctor,
  apiAdminListDoctors,
  apiAdminRunSimulationTask,
  apiAdminSimulationStatus,
} from "../api";

// basic state
const me = ref(null);
const doctors = ref([]);
const message = ref("");
const error = ref("");

// Add doctor form
const form = ref({
  username: "",
  name: "",
  email: "",
  specialization: "",
  password: "",
});

// simulation state
const simulationInfo = ref(null);
const simulationError = ref("");
const simulationLoading = ref(false);

// load initial data
async function load() {
  message.value = "";
  error.value = "";

  try {
    const resMe = await apiGetMe();
    me.value = resMe.data;
  } catch (e) {
    console.error("Error loading /api/me", e);
    error.value = e.response?.data?.error || "Failed to load admin profile";
    return;
  }

  try {
    const resDocs = await apiAdminListDoctors();
    doctors.value = resDocs.data;
  } catch (e) {
    console.error("Error loading admin doctors", e);
    error.value = e.response?.data?.error || "Failed to load doctors";
  }
}

// add doctor
async function addDoctor() {
  message.value = "";
  error.value = "";

  try {
    await apiAdminAddDoctor(form.value);
    message.value = "Doctor added";

    form.value = {
      username: "",
      name: "",
      email: "",
      specialization: "",
      password: "",
    };

    const resDocs = await apiAdminListDoctors();
    doctors.value = resDocs.data;
  } catch (e) {
    console.error("Error adding doctor", e);
    error.value = e.response?.data?.error || "Failed to add doctor";
  }
}

// simulation actions
async function startSimulationTask() {
  simulationError.value = "";
  simulationInfo.value = null;
  simulationLoading.value = true;

  try {
    const res = await apiAdminRunSimulationTask();
    simulationInfo.value = res.data;
  } catch (e) {
    console.error("Error starting simulation task", e);
    simulationError.value =
      e.response?.data?.error || "Failed to start simulation task.";
  } finally {
    simulationLoading.value = false;
  }
}

async function checkSimulationTaskStatus() {
  simulationError.value = "";

  try {
    const res = await apiAdminSimulationStatus();
    simulationInfo.value = res.data;
  } catch (e) {
    console.error("Error checking simulation task status", e);
    simulationError.value =
      e.response?.data?.error || "Failed to fetch simulation status.";
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Admin Dashboard</h3>

    <p v-if="me">Logged in as {{ me.name }} ({{ me.role }})</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- ROW 1: Add Doctor + Doctors List -->
    <div class="row">
      <div class="col-md-6">
        <h5>Add Doctor</h5>
        <form @submit.prevent="addDoctor">
          <div class="mb-2">
            <label class="form-label">Username</label>
            <input v-model="form.username" class="form-control" required />
          </div>
          <div class="mb-2">
            <label class="form-label">Name</label>
            <input v-model="form.name" class="form-control" required />
          </div>
          <div class="mb-2">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="mb-2">
            <label class="form-label">Specialization</label>
            <input v-model="form.specialization" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required />
          </div>
          <button class="btn btn-primary">Save</button>
        </form>
      </div>

      <div class="col-md-6">
        <h5>Doctors</h5>
        <table class="table table-sm">
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
              <td>{{ d.specialization }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ROW 2: Background Simulation -->
    <div class="row mt-4">
      <div class="col-md-8">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title mb-3">Background Simulation</h5>
            <p class="text-muted small mb-3">
              Demonstrates asynchronous processing by running a simulated background task
              (such as generating a system report) without blocking the interface.
            </p>

            <div class="d-flex gap-2 mb-3">
              <button
                type="button"
                class="btn btn-sm btn-primary"
                @click="startSimulationTask"
                :disabled="simulationLoading"
              >
                <span v-if="simulationLoading">Starting simulation...</span>
                <span v-else>Run Simulation Task</span>
              </button>

              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                @click="checkSimulationTaskStatus"
              >
                Check Status
              </button>
            </div>

            <div v-if="simulationError" class="alert alert-danger py-2">
              {{ simulationError }}
            </div>

            <div v-if="simulationInfo" class="alert alert-info py-2 small">
              <div><strong>Message:</strong> {{ simulationInfo.message || simulationInfo.status }}</div>
              <div v-if="simulationInfo.details || simulationInfo.note">
                <strong>Details:</strong> {{ simulationInfo.details || simulationInfo.note }}
              </div>
            </div>

            <div v-else class="text-muted small">
              No simulation has been run yet in this session.
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

