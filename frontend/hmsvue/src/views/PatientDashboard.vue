<script setup>
// SETUP: Imports
import { ref, onMounted, computed } from "vue";
import {
  apiGetMe,
  apiPatientBookAppointment,
  apiPatientListAppointments,
  apiListDoctors,
  apiPatientUpdateAppointment,
} from "../api";

// STATE
const me = ref(null);
const doctors = ref([]);
const appointments = ref([]);
const message = ref("");
const error = ref("");

const form = ref({
  doctor_id: "",
  date: "",
  time: "",
});

const editingApptId = ref(null);

// DERIVED: upcoming vs past
const upcomingAppointments = computed(() =>
  appointments.value.filter((a) => a.status === "Booked")
);

const pastAppointments = computed(() =>
  appointments.value.filter((a) => a.status !== "Booked")
);

// LOAD: profile, doctors, appointments
async function load() {
  error.value = "";
  message.value = "";

  // 1) Profile
  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;
  } catch (e) {
    console.error("Error loading /api/me", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load profile (${e.response?.status || "no status"})`;
    return; // don't continue if user isn't loaded
  }

  // 2) Doctors
  try {
    const resDocs = await apiListDoctors();
    doctors.value = resDocs.data;
  } catch (e) {
    console.error("Error loading /api/doctors", e);
    error.value =
      e.response?.data?.error ||
      `Failed to load doctors (${e.response?.status || "no status"})`;
    // still continue so appointments can load if possible
  }

  // 3) Appointments
  try {
    const resAppts = await apiPatientListAppointments();
    appointments.value = resAppts.data;
  } catch (e) {
    console.error("Error loading /api/patient/appointments", e);
    const backendMsg = e.response?.data?.error || "";
    if (backendMsg) {
      error.value = backendMsg;
    } else {
      appointments.value = [];
    }
  }
}

// HELPER: clear form + editing state
function resetForm() {
  form.value = {
    doctor_id: "",
    date: "",
    time: "",
  };
  editingApptId.value = null;
}

// BOOK / UPDATE: appointment
async function book() {
  error.value = "";
  message.value = "";

  // editing existing appointment (reschedule)
  if (editingApptId.value) {
    try {
      await apiPatientUpdateAppointment(editingApptId.value, {
        date: form.value.date,
        time: form.value.time,
        status: "Booked",
      });
      message.value = "Appointment updated";

      const resAppts = await apiPatientListAppointments();
      appointments.value = resAppts.data;

      resetForm();
    } catch (e) {
      console.error("Error updating appointment", e);
      const backendMsg = e.response?.data?.error || "";

      if (backendMsg.includes("already booked")) {
        error.value =
          "That time slot is already booked. Please choose a different time or doctor.";
      } else if (backendMsg) {
        error.value = backendMsg;
      } else {
        error.value =
          "Could not update the appointment. Please try again in a moment.";
      }
    }

    return;
  }

  // creating a new appointment
  try {
    await apiPatientBookAppointment(form.value);
    message.value = "Appointment booked";

    const resAppts = await apiPatientListAppointments();
    appointments.value = resAppts.data;

    resetForm();
  } catch (e) {
    console.error("Error booking appointment", e);
    const backendMsg = e.response?.data?.error || "";

    if (backendMsg.includes("already booked")) {
      error.value =
        "That time slot is already booked. Please choose a different time or doctor.";
    } else if (backendMsg.includes("Doctor, date and time are required")) {
      error.value = "Please select doctor, date and time before booking.";
    } else if (backendMsg) {
      error.value = backendMsg;
    } else {
      error.value =
        "Could not book the appointment. Please check your connection and try again.";
    }
  }
}

// ACTION: start rescheduling an appointment
function startReschedule(appt) {
  editingApptId.value = appt.id;
  form.value = {
    doctor_id: appt.doctor_id || "", // doctor_id not in response? optional
    date: appt.date,
    time: appt.time,
  };
  message.value = "";
  error.value = "";
}

// ACTION: cancel rescheduling
function cancelEditing() {
  resetForm();
}

// ACTION: cancel appointment (set status = Cancelled)
async function cancelAppointment(appt) {
  const ok = window.confirm(
    "Are you sure you want to cancel this appointment?"
  );
  if (!ok) return;

  error.value = "";
  message.value = "";

  try {
    await apiPatientUpdateAppointment(appt.id, { status: "Cancelled" });
    message.value = "Appointment cancelled";

    const resAppts = await apiPatientListAppointments();
    appointments.value = resAppts.data;

    if (editingApptId.value === appt.id) {
      resetForm();
    }
  } catch (e) {
    console.error("Error cancelling appointment", e);
    const backendMsg = e.response?.data?.error || "";
    if (backendMsg) {
      error.value = backendMsg;
    } else {
      error.value = "Could not cancel the appointment. Please try again.";
    }
  }
}

onMounted(load);
</script>

<template>
  <div>
    <h3 class="mb-3">Patient Dashboard</h3>

    <p v-if="me">Welcome, {{ me.name }}</p>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row">
      <!-- LEFT: Book / Reschedule appointment -->
      <div class="col-md-5">
        <h5>Book Appointment</h5>

        <div
          v-if="editingApptId"
          class="alert alert-info py-2 px-3 mb-2"
        >
          You are rescheduling an existing appointment.
          <button
            type="button"
            class="btn btn-sm btn-link"
            @click="cancelEditing"
          >
            Cancel
          </button>
        </div>

        <form @submit.prevent="book">
          <div class="mb-2">
            <label class="form-label">Doctor</label>
            <select
              v-model="form.doctor_id"
              class="form-select"
              :disabled="!!editingApptId"
              required
            >
              <option value="" disabled>Select doctor</option>
              <option
                v-for="d in doctors"
                :key="d.id"
                :value="d.id"
              >
                {{ d.name }} ({{ d.specialization || "General" }})
              </option>
            </select>
          </div>

          <div class="mb-2">
            <label class="form-label">Date</label>
            <input
              v-model="form.date"
              type="date"
              class="form-control"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Time</label>
            <input
              v-model="form.time"
              type="time"
              class="form-control"
              required
            />
          </div>

          <button class="btn btn-primary">
            {{ editingApptId ? "Save Changes" : "Book" }}
          </button>
        </form>
      </div>

      <!-- RIGHT: Appointment lists -->
      <div class="col-md-7">
        <h5>Upcoming Appointments</h5>
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Status</th>
              <th style="width: 180px">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="upcomingAppointments.length === 0">
              <td colspan="5" class="text-muted text-center">
                No upcoming appointments.
              </td>
            </tr>
            <tr
              v-for="appt in upcomingAppointments"
              :key="appt.id"
            >
              <td>{{ appt.date }}</td>
              <td>{{ appt.time }}</td>
              <td>{{ appt.doctor_name || appt.doctor_username }}</td>
              <td>
                <span class="badge bg-secondary">
                  {{ appt.status }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-outline-primary me-1"
                  @click="startReschedule(appt)"
                >
                  Reschedule
                </button>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="cancelAppointment(appt)"
                >
                  Cancel
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <h5 class="mt-4">Past Appointments</h5>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Status</th>
              <th>Diagnosis</th>
              <th>Prescription</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pastAppointments.length === 0">
              <td colspan="6" class="text-muted text-center">
                No past appointments yet.
              </td>
            </tr>
            <tr
              v-for="appt in pastAppointments"
              :key="appt.id"
            >
              <td>{{ appt.date }}</td>
              <td>{{ appt.time }}</td>
              <td>{{ appt.doctor_name || appt.doctor_username }}</td>
              <td>
                <span
                  class="badge"
                  :class="{
                    'bg-success': appt.status === 'Completed',
                    'bg-danger': appt.status === 'Cancelled',
                    'bg-secondary': appt.status !== 'Completed' && appt.status !== 'Cancelled'
                  }"
                >
                  {{ appt.status }}
                </span>
              </td>
              <td>{{ appt.diagnosis || "-" }}</td>
              <td>{{ appt.prescription || "-" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
