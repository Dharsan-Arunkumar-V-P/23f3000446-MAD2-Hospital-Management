<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Doctor Dashboard</h2>
      <div class="text-end">
        <small class="text-muted">Logged in as {{ me?.name || "Doctor" }} {{ me?.username ? `(${me.username})` : "" }}</small>
      </div>
    </div>

    <!-- API error -->
    <div v-if="apiError" class="alert alert-danger">
      <strong>API load failed.</strong>
      <div class="small">{{ apiErrorMessage }}</div>
      <div class="mt-2">
        <button class="btn btn-sm btn-outline-light" @click="tryImportApi">Retry</button>
      </div>
      <div class="mt-2 small text-muted">Open DevTools → Network/Console to inspect the problem and paste errors here.</div>
    </div>

    <!-- Success toast -->
    <div v-if="toast" class="toast-fixed">
      <div class="toast-body">{{ toast }}</div>
      <button class="toast-close" @click="toast = ''">×</button>
    </div>

    <div v-else>
      <!-- filters -->
      <div class="card-med mb-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-8">
            <input v-model="query" class="form-control" placeholder="Search by patient, date, or time (e.g. pat1, 2025-11-29)" />
          </div>
          <div class="col-md-2">
            <select v-model="statusFilter" class="form-select">
              <option value="">All</option>
              <option>Booked</option>
              <option>Completed</option>
              <option>Cancelled</option>
            </select>
          </div>
          <div class="col-md-2 text-end">
            <button class="btn btn-sm btn-outline-secondary" @click="reloadAll">Refresh</button>
          </div>
        </div>
      </div>

      <!-- improved table -->
      <div class="card-med">
        <h5 class="mb-3">My Appointments</h5>

        <div v-if="loading" class="text-center text-muted p-4">Loading appointments…</div>

        <table v-else class="table table-sm align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th style="min-width:140px">Status</th>
              <th style="min-width:240px">Diagnosis</th>
              <th style="min-width:240px">Prescription</th>
              <th style="width:120px">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="filteredAppts.length===0">
              <td colspan="7" class="text-center text-muted">No appointments found.</td>
            </tr>

            <tr v-for="row in filteredAppts" :key="row.id">
              <td>{{ row.date }}</td>
              <td>{{ row.time }}</td>
              <td>{{ row.patient_name || row.patient }}</td>

              <!-- STATUS -->
              <td>
                <select v-model="row._draft.status" class="form-select form-select-sm" :disabled="row._saving">
                  <option>Booked</option>
                  <option>Completed</option>
                  <option>Cancelled</option>
                </select>
              </td>

              <!-- DIAGNOSIS -->
              <td>
                <input v-model="row._draft.diagnosis" class="form-control form-control-sm" :disabled="row._saving" />
              </td>

              <!-- PRESCRIPTION -->
              <td>
                <input v-model="row._draft.prescription" class="form-control form-control-sm" :disabled="row._saving" />
              </td>

              <!-- ACTIONS -->
              <td class="text-end">
                <div class="d-flex justify-content-end gap-2 align-items-center">
                  <div v-if="row._saving" class="small text-muted">Saving…</div>

                  <button
                    v-else
                    class="btn btn-sm btn-primary"
                    :disabled="!row._changed"
                    @click="saveRow(row)"
                  >
                    Save
                  </button>

                  <button
                    class="btn btn-sm btn-outline-secondary"
                    v-if="row._changed && !row._saving"
                    @click="revertRow(row)"
                    title="Revert changes"
                  >
                    Revert
                  </button>

                  <div class="small text-muted ms-2" v-if="row._lastSaved">Saved: {{ row._lastSaved }}</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- footer quick controls -->
      <div class="mt-3 d-flex justify-content-between align-items-center">
        <div class="small text-muted">Last reload: {{ lastReload || "—" }}</div>
        <div>
          <button class="btn btn-sm btn-outline-secondary" @click="autoToggle">
            Auto-refresh: {{ autoRefresh ? "ON" : "OFF" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from "vue";

/* ---------- API dynamic import (safe) ---------- */
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
      apiErrorMessage.value = e2?.message || e1?.message || "Failed to import api";
      console.error("API import errors:", e1, e2);
      return;
    }
  }
}

/* helper to find function under different names */
function getFn(names) {
  if (!api.value) return null;
  for (const n of names) {
    if (typeof api.value[n] === "function") return api.value[n];
    if (api.value.default && typeof api.value.default[n] === "function") return api.value.default[n];
  }
  return null;
}

/* likely-api functions we'll try to resolve */
let fnGetMe, fnList, fnUpdate;

/* resolve functions after import */
function resolveFns() {
  fnGetMe = getFn(["apiGetMe", "getMe", "get_current_user"]);
  fnList = getFn(["apiDoctorListAppointments", "doctorListAppointments", "listAppointments", "getAppointments"]);
  fnUpdate = getFn(["apiDoctorUpdateAppointment", "doctorUpdateAppointment", "updateAppointment", "patchAppointment"]);
}

/* unwrap helper */
function unwrap(r) { return r?.data ?? r; }

/* ---------- state ---------- */
const me = ref(null);
const appts = ref([]);
const loading = ref(false);
const lastReload = ref("");
const autoRefresh = ref(false);
let autoTimer = null;

const query = ref("");
const statusFilter = ref("");
const toast = ref("");

/* small local metadata we attach to rows for UI */
function attachDraft(a) {
  // keep original for revert
  a._orig = { status: a.status, diagnosis: a.diagnosis ?? "", prescription: a.prescription ?? "" };
  a._draft = { status: a._orig.status, diagnosis: a._orig.diagnosis, prescription: a._orig.prescription };
  a._changed = false;
  a._saving = false;
  a._lastSaved = a._lastSaved ?? ""; // persisted last saved time string
}

/* watch for drafts to compute changed */
function computeChanged(a) {
  a._changed = (
    a._draft.status !== (a._orig.status ?? "") ||
    (a._draft.diagnosis || "") !== (a._orig.diagnosis || "") ||
    (a._draft.prescription || "") !== (a._orig.prescription || "")
  );
}

/* ---------- computed filtered list ---------- */
const filteredAppts = computed(() => {
  let list = Array.isArray(appts.value) ? appts.value : [];

  if (statusFilter.value) list = list.filter(x => x._draft.status === statusFilter.value);

  const q = (query.value || "").trim().toLowerCase();
  if (q) {
    list = list.filter(x => {
      const hay = `${x.date} ${x.time} ${x.patient_name || x.patient} ${x.doctor_name || x.doctor}`.toLowerCase();
      return hay.includes(q);
    });
  }
  return list;
});

/* ---------- fetchers ---------- */
async function fetchMe() {
  if (!fnGetMe) return;
  try {
    const r = unwrap(await fnGetMe());
    me.value = r;
  } catch (err) {
    console.error("fetchMe", err);
  }
}

async function fetchAppointments() {
  if (!fnList) {
    console.error("list fn missing");
    return;
  }
  loading.value = true;
  try {
    // server might accept optional params; pass object if available
    const r = unwrap(await fnList());
    const arr = Array.isArray(r) ? r : (r?.appointments ?? []);
    // attach drafts
    appts.value = arr.map(a => ({ ...a }));
    appts.value.forEach(a => attachDraft(a));
    lastReload.value = new Date().toLocaleString();
  } catch (err) {
    console.error("fetchAppointments", err);
    // don't crash — keep current appts
  } finally {
    loading.value = false;
  }
}

/* ---------- save a row (robust) ---------- */
async function saveRow(row) {
  if (!fnUpdate) {
    toast.value = "Save API not found on server — cannot persist changes.";
    setTimeout(()=> toast.value = "", 3500);
    return;
  }

  // prepare payload: only changed fields
  const payload = { id: row.id };
  if (row._draft.status !== row._orig.status) payload.status = row._draft.status;
  if ((row._draft.diagnosis || "") !== (row._orig.diagnosis || "")) payload.diagnosis = row._draft.diagnosis;
  if ((row._draft.prescription || "") !== (row._orig.prescription || "")) payload.prescription = row._draft.prescription;

  if (Object.keys(payload).length <= 1) {
    // nothing to save
    return;
  }

  // optimistic UI: set saving flag
  row._saving = true;

  // keep backup to rollback on failure
  const backup = { ...row._orig };

  try {
    const r = unwrap(await fnUpdate(row.id, payload));
    // Server might return updated object; prefer server values
    const updated = r && typeof r === "object" ? r : null;

    // update local row with returned values (if present), else use draft
    row.status = updated?.status ?? row._draft.status;
    row.diagnosis = updated?.diagnosis ?? row._draft.diagnosis;
    row.prescription = updated?.prescription ?? row._draft.prescription;

    // refresh original snapshot to match persisted values
    row._orig.status = row.status;
    row._orig.diagnosis = row.diagnosis ?? "";
    row._orig.prescription = row.prescription ?? "";

    row._lastSaved = new Date().toLocaleString();
    row._changed = false;
    toast.value = "Appointment saved";
    setTimeout(()=> toast.value = "", 2400);

    // refresh from server to ensure canonical state (optional but safer)
    await fetchAppointments();
  } catch (err) {
    console.error("saveRow error", err);
    // rollback
    row._orig.status = backup.status;
    row._orig.diagnosis = backup.diagnosis;
    row._orig.prescription = backup.prescription;

    row._draft.status = row._orig.status;
    row._draft.diagnosis = row._orig.diagnosis;
    row._draft.prescription = row._orig.prescription;
    computeChanged(row);

    toast.value = "Save failed — check console/network";
    setTimeout(()=> toast.value = "", 4200);
  } finally {
    row._saving = false;
  }
}

/* revert */
function revertRow(row) {
  row._draft.status = row._orig.status;
  row._draft.diagnosis = row._orig.diagnosis;
  row._draft.prescription = row._orig.prescription;
  computeChanged(row);
}

/* watch draft changes to update _changed */
watch(appts, (newVal) => {
  // whenever appts array replaced attach watchers if needed
  newVal?.forEach(a => {
    computeChanged(a);
  });
}, { deep: true });

/* watch each row's draft to set changed flag dynamically */
function watchDraft(row) {
  watch(() => [row._draft.status, row._draft.diagnosis, row._draft.prescription], () => computeChanged(row));
}

/* reload control */
async function reloadAll() {
  statusFilter.value = "";
  query.value = "";
  await fetchAppointments();
  await fetchMe();
}

/* auto-refresh toggle */
function autoToggle() {
  autoRefresh.value = !autoRefresh.value;
  if (autoRefresh.value) {
    autoTimer = setInterval(() => fetchAppointments(), 30000); // every 30s
  } else {
    clearInterval(autoTimer);
    autoTimer = null;
  }
}

/* ---------- mount ---------- */
onMounted(async () => {
  await tryImportApi();
  if (!api.value) return;
  resolveFns();
  // validate required functions
  if (!fnList || !fnUpdate || !fnGetMe) {
    apiError.value = true;
    apiErrorMessage.value = "Required API functions missing. Check console.";
    console.error("Required API functions missing", { fnList, fnUpdate, fnGetMe });
    return;
  }
  await fetchMe();
  await fetchAppointments();

  // attach watchers for each row
  appts.value.forEach(r => watchDraft(r));
});

/* allow reactive watchers to bind on newly fetched rows */
watch(appts, (newVal) => {
  if (!newVal) return;
  // attach per-row watchers
  newVal.forEach(r => {
    if (!r._draft) attachDraft(r);
    try { watchDraft(r); } catch(e) { /* ignore duplicate watchers */ }
  });
});
</script>

<style scoped>
.card-med { background:#fff; border-radius:12px; padding:14px; box-shadow: 0 6px 18px rgba(11,19,29,0.06); }
.table th, .table td { vertical-align: middle; }

/* toast */
.toast-fixed { position: fixed; right: 20px; top: 80px; z-index: 9999; display:flex; align-items:center; gap:8px; background:#fff; border-radius:8px; box-shadow:0 8px 20px rgba(0,0,0,0.12); padding:8px 12px; }
.toast-body { font-weight:600; }
.toast-close { border:none; background:transparent; font-size:18px; line-height:1; cursor:pointer; }

/* small */
.form-select-sm, .form-control { min-height: 34px; }

/* saving indicator */
.small.text-muted { font-size: 12px; color: #666; }

/* responsive tweaks */
@media (max-width: 780px) {
  .table thead { display: none; }
  .table tbody td { display: block; width: 100%; }
  .table tbody tr { margin-bottom: 12px; display: block; background: #fff; border-radius: 8px; padding: 10px; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }
}
</style>
