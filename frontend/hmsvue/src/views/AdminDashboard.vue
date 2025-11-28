<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="page-title">Admin Dashboard</h3>
      <div class="text-end">
        <small class="text-muted">Logged in as {{ me?.name }}</small>
      </div>
    </div>

    <div class="row row-gap mb-3">
      <!-- FIRST ROW: Appointments (left) + Counts (right) -->
      <div class="col-lg-7">
        <div class="card-med">
          <h5 class="mb-3">Appointments</h5>
          <div class="table-responsive">
            <table class="table table-sm">
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
                <tr v-if="appts.length === 0">
                  <td colspan="5" class="text-center text-muted">No appointments yet.</td>
                </tr>
                <tr v-for="a in appts" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td>{{ a.time }}</td>
                  <td>{{ a.doctor_name }}</td>
                  <td>{{ a.patient_name }}</td>
                  <td>
                    <span class="badge" :class="{'bg-success': a.status==='Completed','bg-danger': a.status==='Cancelled','bg-secondary': a.status==='Booked'}">{{ a.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card-med bg-med-gold">
          <h6>Overview</h6>
          <div class="d-flex flex-column gap-2">
            <div class="d-flex justify-content-between align-items-center py-2">
              <div>
                <div class="text-muted small">Doctors</div>
                <div class="h5 mb-0">{{ summary.total_doctors }}</div>
              </div>
              <div class="text-end">
                <small class="text-muted">Patients</small>
                <div class="h5">{{ summary.total_patients }}</div>
              </div>
            </div>
            <div class="d-flex justify-content-between align-items-center py-2">
              <div>
                <div class="text-muted small">Appointments</div>
                <div class="h5 mb-0">{{ summary.total_appointments }}</div>
              </div>
              <div>
                <div class="text-muted small">Booked</div>
                <div class="h6 mb-0">{{ summary.booked }}</div>
              </div>
            </div>
            <div class="d-flex justify-content-between align-items-center py-2">
              <div>
                <div class="text-muted small">Completed</div>
                <div class="h6 mb-0">{{ summary.completed }}</div>
              </div>
              <div>
                <div class="text-muted small">Cancelled</div>
                <div class="h6 mb-0">{{ summary.cancelled }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SECOND ROW: Add Doctor (left) + Doctor List (right) -->
    <div class="row row-gap mb-3">
      <div class="col-lg-7">
        <div class="card-med">
          <h5 class="mb-3">Add Doctor</h5>
          <form @submit.prevent="addDoctor">
            <div class="row g-2">
              <div class="col-sm-6">
                <input v-model="form.username" class="form-control" placeholder="Username" required />
              </div>
              <div class="col-sm-6">
                <input v-model="form.name" class="form-control" placeholder="Name" required />
              </div>
              <div class="col-sm-6">
                <input v-model="form.email" type="email" class="form-control" placeholder="Email" />
              </div>
              <div class="col-sm-6">
                <input v-model="form.specialization" class="form-control" placeholder="Specialization" />
              </div>
              <div class="col-sm-6 mt-2">
                <input v-model="form.password" type="password" class="form-control" placeholder="Password" required />
              </div>
              <div class="col-sm-6 mt-2 text-end">
                <button class="btn btn-primary">Save</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card-med">
          <h5 class="mb-3">Doctors</h5>
          <div class="list-group">
            <div class="list-group-item" v-for="d in doctors" :key="d.id">
              <div class="d-flex justify-content-between">
                <div>
                  <strong>{{ d.name }}</strong>
                  <div class="text-muted small">{{ d.specialization || 'General' }}</div>
                </div>
                <div class="text-end small">
                  <div>{{ d.username }}</div>
                  <div class="text-muted">{{ d.email }}</div>
                </div>
              </div>
            </div>
            <div v-if="doctors.length===0" class="text-center text-muted p-3">No doctors yet.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- BOTTOM: Simulation task (full width) -->
    <div class="row">
      <div class="col-12">
        <div class="card-med">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-0">Simulation Runner</h5>
              <div class="text-muted small">Run background simulations (no external workers required)</div>
            </div>
            <div class="text-end">
              <button class="btn btn-outline-primary me-2" @click="checkSimulation">Status</button>
              <button class="btn btn-primary" @click="runSimulation">Run Simulation</button>
            </div>
          </div>
          <div v-if="simMessage" class="mt-2 alert alert-info">{{ simMessage }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { apiGetMe, apiAdminListDoctors, apiAdminAddDoctor, apiAdminRunSimulationTask, apiAdminSimulationStatus, apiAdminListAppointments, apiAdminSummary } from "../api";

const me = ref(null);
const doctors = ref([]);
const appts = ref([]);
const summary = ref({ total_doctors:0, total_patients:0, total_appointments:0, booked:0, completed:0, cancelled:0});
const simMessage = ref("");

const form = ref({ username: "", name: "", email: "", specialization: "", password: "" });

async function load() {
  try {
    const r = await apiGetMe(); me.value = r.data;
    const rd = await apiAdminListDoctors(); doctors.value = rd.data;
    const ra = await apiAdminListAppointments(); appts.value = ra.data;
    const rs = await apiAdminSummary(); summary.value = rs.data;
  } catch(e) {
    console.error(e);
  }
}

async function addDoctor() {
  try {
    await apiAdminAddDoctor(form.value);
    form.value = { username: "", name: "", email: "", specialization: "", password: "" };
    await load();
  } catch(e) { console.error(e); }
}

async function runSimulation() {
  try {
    const r = await apiAdminRunSimulationTask();
    simMessage.value = r.data.message || "Simulation started";
  } catch(err) { simMessage.value = "Failed to start simulation"; }
}

async function checkSimulation() {
  try {
    const r = await apiAdminSimulationStatus();
    simMessage.value = r.data.status || "No information";
  } catch(err) { simMessage.value = "Failed to check status"; }
}

onMounted(load);
</script>

<style scoped>
/* small spacing tweaks */
.list-group-item { border-radius: 8px; margin-bottom: 8px; }
</style>
