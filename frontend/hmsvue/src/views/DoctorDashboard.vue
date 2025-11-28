<script setup>
import { ref, computed, onMounted } from "vue";
import {
  apiGetMe,
  apiDoctorListAppointments,
  apiDoctorUpdateAppointment,
} from "../api";

const me = ref(null);
const appointments = ref([]);
const loading = ref(false);
const message = ref("");
const error = ref("");

// filters
const search = ref("");
const statusFilter = ref("");

// load doctor + appointments
async function load() {
  message.value = "";
  error.value = "";
  loading.value = true;

  try {
    const resMe = await apiGetMe();
    me.value = resMe.data;
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
    console.error("Error loading doctor appointments", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load appointments (${e.response?.status || "no status"})`;
  } finally {
    loading.value = false;
  }
}

// computed: filtered appointments
const filteredAppointments = computed(() => {
  const term = search.value.trim().toLowerCase();
  const status = statusFilter.value;

  return appointments.value.filter((a) => {
    const matchesStatus = !status || a.status === status;

    const combined = `${a.date} ${a.time} ${a.patient_name || ""} ${
      a.patient_username || ""
    }`.toLowerCase();

    const matchesSearch = !term || combined.includes(term);

    return matchesStatus && matchesSearch;
  });
});

// save appointment changes (diagnosis / prescription / status)
async function saveAppointment(appt) {
  message.value = "";
  error.value = "";

  try {
    await apiDoctorUpdateAppointment(appt.id, {
      diagnosis: appt.diagnosis || "",
      prescription: appt.prescription || "",
      status: appt.status || "Completed",
    });

    message.value = "Appointment updated";
  } catch (e) {
    console.error("Error updating appointment", e);
    error.value =
      e.response?.data?.error ||
      `Failed to update appointment (${e.response?.status || "no status"})`;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Doctor Dashboard</h3>

    <p v-if="me">Logged in as Dr. {{ me.name }} ({{ me.username }})</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Filters -->
    <div class="card mb-3 shadow-sm">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col-md-6">
            <label class="form-label small text-muted mb-1">
              Search by patient, date, or time
            </label>
            <input
              v-model="search"
              class="form-control form-control-sm"
              placeholder="e.g. pat1, John, 2025-11-28..."
            />
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">
              Status
            </label>
            <select
              v-model="statusFilter"
              class="form-select form-select-sm"
            >
              <option value="">All</option>
              <option value="Booked">Booked</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-3 text-md-end mt-2 mt-md-0">
            <button
              class="btn btn-sm btn-outline-secondary"
              type="button"
              @click="load"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments table -->
    <div class="card shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-3">My Appointments</h5>

        <div v-if="loading" class="text-muted">
          Loading appointments…
        </div>

        <div v-else class="table-responsive">
          <table class="table table-sm align-middle">
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Patient</th>
                <th>Status</th>
                <th style="min-width: 160px;">Diagnosis</th>
                <th style="min-width: 160px;">Prescription</th>
                <th style="width: 110px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredAppointments.length === 0">
                <td colspan="7" class="text-muted text-center small">
                  No appointments found for the current filters.
                </td>
              </tr>
              <tr
                v-for="appt in filteredAppointments"
                :key="appt.id"
              >
                <td>{{ appt.date }}</td>
                <td>{{ appt.time }}</td>
                <td>
                  {{ appt.patient_name || appt.patient_username || "-" }}
                </td>
                <td style="max-width: 140px;">
                  <select
                    v-model="appt.status"
                    class="form-select form-select-sm"
                  >
                    <option value="Booked">Booked</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                </td>
                <td>
                  <input
                    v-model="appt.diagnosis"
                    class="form-control form-control-sm"
                    placeholder="Diagnosis"
                  />
                </td>
                <td>
                  <input
                    v-model="appt.prescription"
                    class="form-control form-control-sm"
                    placeholder="Prescription"
                  />
                </td>
                <td class="text-end">
                  <button
                    class="btn btn-sm btn-primary"
                    type="button"
                    @click="saveAppointment(appt)"
                  >
                    Save
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>
