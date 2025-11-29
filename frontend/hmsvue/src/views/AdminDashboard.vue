<template>
  <div>
    <!-- HEADER -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="page-title">Medaleon — Admin Dashboard</h3>
      <div class="text-end">
        <small class="text-muted">Logged in as {{ me?.name || "—" }}</small>
      </div>
    </div>

    <!-- API IMPORT ERROR -->
    <div v-if="apiError" class="alert alert-danger">
      <strong>Failed to load API module.</strong>
      <div class="small">{{ apiErrorMessage }}</div>
      <button class="btn btn-sm btn-outline-light mt-2" @click="tryImportApi">Retry</button>
    </div>

    <div v-else>
      <div class="row">
        
        <!-- LEFT COLUMN -->
        <div class="col-lg-8">
          
          <!-- APPOINTMENTS -->
          <div class="card-med mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <h5 class="mb-0">Appointments</h5>
                <small class="text-muted">Latest appointments</small>
              </div>

              <div class="d-flex gap-2">
                <input v-model="search" class="form-control form-control-sm" placeholder="Search..." />
                <select v-model="sortKey" class="form-select form-select-sm" style="width:140px">
                  <option value="">Sort</option>
                  <option value="date_asc">Date ↑</option>
                  <option value="date_desc">Date ↓</option>
                  <option value="time_asc">Time ↑</option>
                  <option value="time_desc">Time ↓</option>
                </select>
                <button class="btn btn-sm btn-outline-secondary" @click="refreshAppointments">Refresh</button>
              </div>
            </div>

            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Date</th><th>Time</th><th>Doctor</th><th>Patient</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  
                  <tr v-if="loadingAppts">
                    <td colspan="5" class="text-center text-muted">Loading…</td>
                  </tr>

                  <tr v-else-if="apptsFiltered.length === 0">
                    <td colspan="5" class="text-center text-muted">No appointments found.</td>
                  </tr>

                  <tr v-for="a in apptsFiltered" :key="a.id">
                    <td>{{ a.date }}</td>
                    <td>{{ a.time }}</td>
                    <td>{{ a.doctor_name || "-" }}</td>
                    <td>{{ a.patient_name || "-" }}</td>
                    <td>
                      <span
                        class="badge status-pill"
                        :class="{
                          'bg-success': a.status === 'Completed',
                          'bg-danger': a.status === 'Cancelled',
                          'bg-secondary': a.status === 'Booked'
                        }"
                        @click="filterByStatus(a.status)"
                        style="cursor:pointer"
                      >
                        {{ a.status }}
                      </span>
                    </td>
                  </tr>

                </tbody>
              </table>
            </div>
          </div>

          <!-- PATIENTS -->
          <div class="card-med mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Patients</h5>
              <small class="text-muted">{{ patientsUnique.length }} unique</small>
            </div>

            <div v-if="patientsUnique.length === 0" class="text-muted p-3">No patients yet.</div>

            <div class="list-group" v-else>
              <div class="list-group-item" v-for="p in patientsUnique" :key="p">{{ p }}</div>
            </div>
          </div>

          <!-- DOCTORS -->
          <div class="card-med">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h5 class="mb-0">Doctors</h5>
              <button class="btn btn-sm"
                      :class="editMode ? 'btn-outline-danger' : 'btn-outline-secondary'"
                      @click="toggleEditMode">
                {{ editMode ? "Edit: ON" : "Edit: OFF" }}
              </button>
            </div>

            <div v-if="doctors.length === 0" class="p-3 text-muted text-center">No doctors yet.</div>

            <div v-else class="list-group">
              <div class="list-group-item d-flex justify-content-between" v-for="d in doctors" :key="d.id">
                
                <div>
                  <strong>{{ d.name }}</strong>
                  <div class="small text-muted">{{ d.specialization || "General" }}</div>
                </div>

                <div class="text-end small">
                  <div>{{ d.username }}</div>
                  <div class="text-muted">{{ d.email }}</div>

                  <div v-if="editMode" class="d-flex gap-2 mt-2 justify-content-end">
                    <button class="btn btn-sm btn-outline-primary" @click="openEdit(d)">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" @click="confirmRemove(d)">Remove</button>
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>

        <!-- RIGHT COLUMN -->
        <div class="col-lg-4">

          <!-- OVERVIEW -->
          <div class="card-med mb-3">
            <div class="d-flex justify-content-between">
              <h6 class="mb-2">Overview</h6>
              <button class="btn btn-sm btn-outline-secondary" @click="refreshAll">
                {{ loadingSummary ? "…" : "Refresh" }}
              </button>
            </div>

            <div class="overview-grid-3col">
              
              <div class="stat stat-large">
                <div class="stat-label">Appointments</div>
                <div class="stat-value">{{ summary.total_appointments }}</div>
              </div>

              <div class="stat stat-large">
                <div class="stat-label">Patients</div>
                <div class="stat-value">{{ summary.total_patients }}</div>
              </div>

              <div class="stat stat-large">
                <div class="stat-label">Doctors</div>
                <div class="stat-value">{{ summary.total_doctors }}</div>
              </div>

              <div class="stat clickable" @click="filterByStatus('Completed')">
                <div class="stat-label">Completed</div>
                <div class="stat-value text-success">{{ summary.completed }}</div>
              </div>

              <div class="stat clickable" @click="filterByStatus('Booked')">
                <div class="stat-label">Booked</div>
                <div class="stat-value text-danger">{{ summary.booked }}</div>
              </div>

              <div class="stat clickable" @click="filterByStatus('Cancelled')">
                <div class="stat-label">Cancelled</div>
                <div class="stat-value text-muted">{{ summary.cancelled }}</div>
              </div>

            </div>
          </div>

          <!-- ACTIONS -->
          <div class="card-med mb-3">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Actions</h6>
              <button class="btn btn-sm btn-primary" @click="toggleAddForm">
                {{ showAddForm ? "Close" : "+ Add Doctor" }}
              </button>
            </div>

            <div v-if="showAddForm" class="mt-3">
              <form @submit.prevent="addDoctor">
                <input v-model="form.username" class="form-control form-control-sm mb-2" placeholder="Username" required />
                <input v-model="form.name" class="form-control form-control-sm mb-2" placeholder="Name" required />
                <input v-model="form.email" class="form-control form-control-sm mb-2" placeholder="Email" />
                <input v-model="form.specialization" class="form-control form-control-sm mb-2" placeholder="Specialization" />
                <input v-model="form.password" type="password" class="form-control form-control-sm mb-3" placeholder="Password" required />

                <div class="d-flex justify-content-end gap-2">
                  <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleAddForm">Cancel</button>
                  <button class="btn btn-sm btn-primary" :disabled="addingDoctor">{{ addingDoctor ? "Saving…" : "Save" }}</button>
                </div>

                <div v-if="addError" class="text-danger small mt-2">{{ addError }}</div>
              </form>
            </div>
          </div>

          <!-- SIMULATION -->
          <div class="card-med">
            <h6 class="mb-2">Simulation Runner</h6>

            <p class="small text-muted mb-2">
              Runs backend scheduling simulation. Helps test booking/cancel scenarios safely.
            </p>

            <div class="d-flex gap-2 mb-2">
              <button class="btn btn-sm btn-outline-primary" @click="checkSimulation">{{ checkingSim ? "..." : "Status" }}</button>
              <button class="btn btn-sm btn-primary" @click="runSimulation" :disabled="runningSim">{{ runningSim ? "..." : "Run" }}</button>
            </div>

            <div v-if="simMessage" class="mt-2">
              <div class="small text-muted">Message:</div>
              <div class="alert alert-info p-2 mb-1">{{ simMessage }}</div>
              <div class="small text-muted">Timestamp: {{ lastSimRun || "—" }}</div>
            </div>

            <div v-else class="small text-muted">No simulation run yet.</div>
          </div>

        </div>
      </div>

      <!-- EDIT MODAL -->
      <div v-if="editing" class="modal-backdrop">
        <div class="modal-card card-med p-4">
          <h5>Edit Doctor</h5>
          <form @submit.prevent="saveEdit">
            <input v-model="editForm.name" class="form-control mb-2" placeholder="Name" required />
            <input v-model="editForm.specialization" class="form-control mb-3" placeholder="Specialization" />
            <div class="d-flex justify-content-end gap-2">
              <button class="btn btn-outline-secondary" @click="closeEdit" type="button">Cancel</button>
              <button class="btn btn-primary" type="submit">Save</button>
            </div>
          </form>
        </div>
      </div>

      <!-- REMOVE MODAL -->
      <div v-if="removing" class="modal-backdrop">
        <div class="modal-card card-med p-4">
          <h5>Remove Doctor</h5>
          <p class="mb-3">
            Are you sure you want to remove <strong>{{ removing.name }}</strong>?
          </p>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-outline-secondary" @click="cancelRemove">Cancel</button>
            <button class="btn btn-danger" @click="removeDoctor">Remove</button>
          </div>
        </div>
      </div>

    </div>

    <!-- TOAST -->
    <div v-if="toast" class="toast-box">{{ toast }}</div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";

/*
   API IMPORT (Safe dynamic import + fallback)

*/
const api = ref(null);
const apiError = ref(false);
const apiErrorMessage = ref("");

async function tryImportApi() {
  apiError.value = false;
  api.value = null;
  try {
    api.value = await import("@/api");
  } catch (e1) {
    try {
      api.value = await import("../api.js");
    } catch (e2) {
      apiError.value = true;
      apiErrorMessage.value = e2.message || e1.message;
      console.error("API import failed:", e1, e2);
      return;
    }
  }
}

function getFn(names) {
  if (!api.value) return null;
  for (const n of names) {
    if (typeof api.value[n] === "function") return api.value[n];
    if (api.value.default && typeof api.value.default[n] === "function")
      return api.value.default[n];
  }
  return null;
}

/* Resolve API functions */
let fnGetMe, fnListDoctors, fnAddDoctor, fnUpdateDoctor, fnRemoveDoctor,
    fnListAppointments, fnSummary, fnRunSim, fnSimStatus;

function resolveApiFns() {
  fnGetMe = getFn(["apiGetMe", "getMe"]);
  fnListDoctors = getFn(["apiAdminListDoctors", "listDoctors"]);
  fnAddDoctor = getFn(["apiAdminAddDoctor", "addDoctor"]);
  fnUpdateDoctor = getFn(["apiAdminUpdateDoctor", "updateDoctor"]);
  fnRemoveDoctor = getFn(["apiAdminRemoveDoctor", "removeDoctor"]);
  fnListAppointments = getFn(["apiAdminListAppointments", "listAppointments"]);
  fnSummary = getFn(["apiAdminSummary", "summary"]);
  fnRunSim = getFn(["apiAdminRunSimulationTask", "runSimulation"]);
  fnSimStatus = getFn(["apiAdminSimulationStatus", "simulationStatus"]);
}

function unwrap(r) {
  return r?.data ?? r;
}

/*
   STATE

*/
const me = ref(null);
const doctors = ref([]);
const appts = ref([]);
const summary = reactive({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  booked: 0,
  completed: 0,
  cancelled: 0,
});

const search = ref("");
const sortKey = ref("");
const statusFilter = ref("");

const loadingAppts = ref(false);
const loadingSummary = ref(false);

const showAddForm = ref(false);
const editMode = ref(false);

const addingDoctor = ref(false);
const addError = ref("");

const simMessage = ref("");
const lastSimRun = ref("");

const runningSim = ref(false);
const checkingSim = ref(false);

const editing = ref(false);
const editForm = reactive({ id: null, name: "", specialization: "" });

const removing = ref(null);

const form = reactive({
  username: "",
  name: "",
  email: "",
  specialization: "",
  password: "",
});

/* Toast */
const toast = ref("");
function showToast(msg) {
  toast.value = msg;
  setTimeout(() => (toast.value = ""), 2200);
}

/*
   COMPUTED

*/
const patientsUnique = computed(() => {
  const set = new Set();
  for (const a of appts.value) {
    const p = a.patient_name;
    if (p && p.trim()) set.add(p.trim());
  }
  return [...set];
});

const apptsFiltered = computed(() => {
  let list = [...appts.value];

  if (statusFilter.value) {
    list = list.filter((a) => a.status === statusFilter.value);
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter((a) =>
      `${a.date} ${a.time} ${a.doctor_name} ${a.patient_name}`
        .toLowerCase()
        .includes(q)
    );
  }

  // correct absolute sorting using real Date objects
  const dt = (a) => new Date(`${a.date} ${a.time}`);

  switch (sortKey.value) {
    case "date_asc":
      list.sort((a, b) => dt(a) - dt(b));
      break;
    case "date_desc":
      list.sort((a, b) => dt(b) - dt(a));
      break;
    case "time_asc":
      list.sort((a, b) => a.time.localeCompare(b.time));
      break;
    case "time_desc":
      list.sort((a, b) => b.time.localeCompare(a.time));
      break;
  }

  return list;
});

/*
   FETCHERS

*/
async function fetchMe() {
  if (!fnGetMe) return;
  try {
    const r = unwrap(await fnGetMe());
    me.value = r?.user || r || me.value;
  } catch (err) {
    console.error("fetchMe:", err);
  }
}

async function fetchDoctors() {
  if (!fnListDoctors) return;
  try {
    const r = unwrap(await fnListDoctors());
    doctors.value = r?.doctors || r || [];
  } catch (err) {
    console.error("fetchDoctors:", err);
  }
}

async function fetchAppointments(status = "") {
  if (!fnListAppointments) return;
  loadingAppts.value = true;
  try {
    const r = unwrap(await fnListAppointments(status ? { status } : undefined));
    appts.value = r?.appointments || r || [];
  } catch (err) {
    console.error("fetchAppointments:", err);
  } finally {
    loadingAppts.value = false;
  }
}

async function fetchSummary() {
  if (!fnSummary) return;
  loadingSummary.value = true;
  try {
    const r = unwrap(await fnSummary());
    if (r) Object.assign(summary, r);
  } catch (err) {
    console.error("fetchSummary:", err);
  } finally {
    loadingSummary.value = false;
  }
}

/*
   ACTIONS

*/
async function refreshAll() {
  search.value = "";
  statusFilter.value = "";
  sortKey.value = "";
  await Promise.all([fetchSummary(), fetchAppointments(), fetchDoctors()]);
  showToast("Refreshed");
}

function refreshAppointments() {
  search.value = "";
  statusFilter.value = "";
  sortKey.value = "";
  fetchAppointments();
}

function filterByStatus(status) {
  statusFilter.value = status;
  fetchAppointments(status);
}

/* ========== ADD DOCTOR ========== */
async function addDoctor() {
  if (!fnAddDoctor) {
    addError.value = "Add API not available";
    return;
  }

  addingDoctor.value = true;
  addError.value = "";

  try {
    const payload = { ...form };
    const res = unwrap(await fnAddDoctor(payload));

    if (res?.error) throw new Error(res.error);

    Object.assign(form, { username: "", name: "", email: "", specialization: "", password: "" });
    showAddForm.value = false;

    await refreshAll();
    showToast("Doctor added");

  } catch (err) {
    console.error("addDoctor:", err);
    addError.value = err.message || "Failed to add doctor";
  } finally {
    addingDoctor.value = false;
  }
}

function toggleAddForm() {
  showAddForm.value = !showAddForm.value;
}

function toggleEditMode() {
  editMode.value = !editMode.value;
}

/* ========== EDIT DOCTOR ========== */
function openEdit(d) {
  editForm.id = d.id;
  editForm.name = d.name;
  editForm.specialization = d.specialization || "";
  editing.value = true;
}

function closeEdit() {
  editing.value = false;
  editForm.id = null;
  editForm.name = "";
  editForm.specialization = "";
}

async function saveEdit() {
  if (!fnUpdateDoctor) return;
  try {
    const res = unwrap(
      await fnUpdateDoctor(editForm.id, {
        name: editForm.name,
        specialization: editForm.specialization,
      })
    );

    if (res?.error) throw new Error(res.error);

    editing.value = false;
    await Promise.all([fetchDoctors(), fetchSummary()]);
    showToast("Doctor updated");

  } catch (err) {
    console.error("saveEdit:", err);
    showToast("Failed to update");
  }
}

/* ========== REMOVE DOCTOR ========== */
function confirmRemove(d) {
  removing.value = d;
}

function cancelRemove() {
  removing.value = null;
}

async function removeDoctor() {
  if (!fnRemoveDoctor) return;

  try {
    const res = unwrap(await fnRemoveDoctor(removing.value.id));
    if (res?.error) throw new Error(res.error);

    removing.value = null;
    await Promise.all([fetchDoctors(), fetchSummary()]);
    showToast("Doctor removed");

  } catch (err) {
    console.error("removeDoctor:", err);
    showToast("Failed to remove");
  }
}

/* ========== SIMULATION ========== */
async function runSimulation() {
  if (!fnRunSim) {
    simMessage.value = "Simulation API missing";
    return;
  }

  runningSim.value = true;

  try {
    const r = unwrap(await fnRunSim());
    simMessage.value = r?.message || "Simulation started";
    lastSimRun.value = new Date().toLocaleString();
  } catch (err) {
    console.error("runSimulation:", err);
    simMessage.value = "Failed to start simulation";
  } finally {
    runningSim.value = false;
  }
}

async function checkSimulation() {
  if (!fnSimStatus) {
    simMessage.value = "Simulation status API missing";
    return;
  }

  checkingSim.value = true;

  try {
    const r = unwrap(await fnSimStatus());
    simMessage.value = r?.status || r?.message || "No info";
    lastSimRun.value = new Date().toLocaleString();
  } catch (err) {
    console.error("checkSimulation:", err);
    simMessage.value = "Failed to check status";
  } finally {
    checkingSim.value = false;
  }
}

/*
   MOUNT

*/
onMounted(async () => {
  await tryImportApi();
  if (!api.value) return;

  resolveApiFns();

  if (!fnGetMe || !fnListDoctors || !fnListAppointments || !fnSummary) {
    apiError.value = true;
    apiErrorMessage.value = "Required API functions missing.";
    return;
  }

  await fetchMe();
  await refreshAll();
});
</script>

<style scoped>
.card-med {
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(11,19,29,0.06);
  margin-bottom: 16px;
}

.status-pill {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 20px;
}

.overview-grid-3col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 10px;
  transition: 0.12s;
}

.stat:hover {
  transform: translateY(-2px);
  background: #f2f2f2;
}

.stat-label {
  color: #666;
  font-size: 13px;
}

.stat-value {
  font-weight: 700;
  font-size: 20px;
}

.list-group-item {
  border-radius: 10px;
  margin-bottom: 10px;
  transition: 0.12s;
}

.list-group-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-card {
  background: #fff;
  width: 420px;
  border-radius: 10px;
  padding: 14px;
}

.toast-box {
  position: fixed;
  bottom: 22px;
  right: 22px;
  padding: 10px 16px;
  background: #333;
  color: #fff;
  border-radius: 8px;
  z-index: 999999;
  opacity: 0.9;
}
</style>
