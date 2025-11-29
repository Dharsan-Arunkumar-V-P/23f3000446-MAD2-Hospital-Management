<script setup>
/*
  OverviewCard.vue
  - Fetches admin summary via apiAdminSummary() from src/api.js
  - Emits "filter-status" with status string when user clicks a status tile
*/

import { ref, onMounted } from "vue";
import { apiAdminSummary } from "@/api"; // uses your api.js helper (already in project). :contentReference[oaicite:2]{index=2}

const loading = ref(true);
const error = ref("");
const summary = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  booked: 0,
  completed: 0,
  cancelled: 0,
});

async function loadSummary() {
  loading.value = true;
  error.value = "";
  try {
    const resp = await apiAdminSummary();
    // axios response object (data at resp.data)
    Object.assign(summary.value, resp.data);
  } catch (err) {
    console.error("Error loading summary:", err);
    error.value = err?.response?.data?.error || "Failed to load summary";
  } finally {
    loading.value = false;
  }
}

// emit events to parent (filter actions)
const emit = defineEmits(["filter-status"]);

function onStatusClick(status) {
  // If user clicks the status tile, notify parent
  emit("filter-status", status);
}

onMounted(() => {
  loadSummary();
});
</script>

<template>
  <div class="card-med overview-card" role="region" aria-label="Admin overview">
    <div class="flex items-center justify-between mb-3">
      <h4 class="page-title">Overview</h4>
      <button class="btn-outline-primary text-xs px-3 py-1" @click="loadSummary" :disabled="loading">
        {{ loading ? "Refreshing…" : "Refresh" }}
      </button>
    </div>

    <div v-if="loading" class="text-sm text-gray-500">Loading summary…</div>
    <div v-else-if="error" class="text-sm text-red-600">{{ error }}</div>

    <div v-else class="overview-grid">
      <!-- Row 1 -->
      <div class="stat-row">
        <div class="stat">
          <span class="stat-label">Doctors</span>
          <span class="stat-value">{{ summary.total_doctors }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Patients</span>
          <span class="stat-value">{{ summary.total_patients }}</span>
        </div>
      </div>

      <!-- Row 2 -->
      <div class="stat-row">
        <div class="stat">
          <span class="stat-label">Appointments</span>
          <span class="stat-value">{{ summary.total_appointments }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Booked</span>
          <button
            class="status-pill status-booked"
            @click="onStatusClick('Booked')"
            aria-pressed="false"
            title="Filter by Booked">
            {{ summary.booked }}
          </button>
        </div>
      </div>

      <!-- Row 3 -->
      <div class="stat-row">
        <div class="stat">
          <span class="stat-label">Completed</span>
          <button
            class="status-pill status-completed"
            @click="onStatusClick('Completed')"
            title="Filter by Completed">
            {{ summary.completed }}
          </button>
        </div>

        <div class="stat">
          <span class="stat-label">Cancelled</span>
          <button
            class="status-pill status-cancelled"
            @click="onStatusClick('Cancelled')"
            title="Filter by Cancelled">
            {{ summary.cancelled }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Leverage your theme.css classes (card-med, page-title) while adding a few layout helpers */
.overview-card { padding: 16px; }
.overview-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr;
}

/* Each row holds two stats (label + value) */
.stat-row { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.stat { display:flex; justify-content:space-between; width:100%; align-items:center; }
.stat-label { color: #6b7280; font-size: 13px; }
.stat-value { font-size: 18px; font-weight: 600; color: #222; }

/* status pills (small clickable) */
.status-pill {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 13px;
  border: none;
  cursor: pointer;
}

/* use your brand colors (defined in theme.css) — these class names follow that file */
.status-booked {
  background: #d32f2f;
  color: white;
}
.status-completed {
  background: #2e7d32;
  color: white;
}
.status-cancelled {
  background: #6b7280;
  color: white;
}

/* small responsive tweak */
@media (max-width: 640px) {
  .overview-grid { gap: 8px; }
  .stat-value { font-size: 16px; }
}
</style>
