<script setup>
// SETUP: Imports
import { ref } from "vue";
import { useRouter } from "vue-router";
import { apiRegister } from "../api";

// INIT: State
const router = useRouter();
const username = ref("");
const name = ref("");
const email = ref("");
const password = ref("");
const error = ref("");
const message = ref("");

// PROCESS: Handle register
async function handleRegister() {
  error.value = "";
  message.value = "";

  try {
    await apiRegister({
      username: username.value,
      name: name.value,
      email: email.value,
      password: password.value,
    });

    message.value = "Registration successful. You can now log in.";
    setTimeout(() => router.push({ name: "login" }), 1000);
  } catch (e) {
    error.value = e.response?.data?.error || "Registration failed";
  }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h3 class="mb-4 text-center">Patient Registration</h3>

      <div v-if="message" class="alert alert-success">{{ message }}</div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input v-model="username" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Name</label>
          <input v-model="name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="email" type="email" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" required />
        </div>

        <button class="btn btn-primary w-100">Register</button>
      </form>

      <p class="mt-3 text-center">
        Already have an account?
        <a href="" @click.prevent="$router.push({ name: 'login' })">
          Go to login
        </a>
      </p>
    </div>
  </div>
</template>
