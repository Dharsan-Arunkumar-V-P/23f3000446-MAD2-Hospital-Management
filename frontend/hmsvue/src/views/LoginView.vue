<script setup>
// SETUP: Imports
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { apiLogin } from "../api";

// INIT: State
const router = useRouter();
const username = ref("");
const password = ref("");
const error = ref("");

// INIT: Clear any old session when opening login
onMounted(() => {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  window.dispatchEvent(new Event("auth-changed"));
});

// PROCESS: Handle login
async function handleLogin() {
  error.value = "";

  try {
    const res = await apiLogin(username.value, password.value);

    localStorage.setItem("token", res.data.token);
    localStorage.setItem("role", res.data.role);
    window.dispatchEvent(new Event("auth-changed"));

    if (res.data.role === "admin") {
      router.push({ name: "admin" });
    } else if (res.data.role === "doctor") {
      router.push({ name: "doctor" });
    } else {
      router.push({ name: "patient" });
    }
  } catch (e) {
    error.value = e.response?.data?.error || "Login failed";
  }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h3 class="mb-4 text-center">Login</h3>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input v-model="username" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Password</label>
          <input
            v-model="password"
            type="password"
            class="form-control"
            required
          />
        </div>

        <button class="btn btn-primary w-100">Login</button>
      </form>

      <p class="mt-3 text-center">
        New patient?
        <a href="" @click.prevent="$router.push({ name: 'register' })">
          Register here
        </a>
      </p>
    </div>
  </div>
</template>
