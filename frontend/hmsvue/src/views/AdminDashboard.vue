<script setup>
import { onMounted, ref } from "vue";
import { apiAdminListDoctors, apiAdminAddDoctor, apiGetMe } from "../api";

// INIT: State
const doctors = ref([]);
const me = ref(null);
const form = ref({
  username: "",
  name: "",
  email: "",
  specialization: "",
  password: "",
});
const message = ref("");
const error = ref("");

// PROCESS: Load data
async function load() {
  try {
    const resUser = await apiGetMe();
    me.value = resUser.data;

    const resDocs = await apiAdminListDoctors();
    doctors.value = resDocs.data;
  } catch {
    error.value = "Failed to load data";
  }
}

// PROCESS: Add doctor
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
    await load();
  } catch (e) {
    error.value = e.response?.data?.error || e.response?.data?.message || "Failed to add doctor";
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
  </div>
</template>
