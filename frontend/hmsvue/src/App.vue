<script setup>
// SETUP: Imports
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";

// INIT: Router + route
const route = useRoute();
const router = useRouter();

// INIT: Reactive auth state
const isLoggedIn = ref(false);
const role = ref(null);

// PROCESS: Sync auth state from localStorage
function syncAuth() {
  isLoggedIn.value = !!localStorage.getItem("token");
  role.value = localStorage.getItem("role");
}

// INIT: Set up listener for global "auth-changed" events
onMounted(() => {
  syncAuth();
  window.addEventListener("auth-changed", syncAuth);
});

onBeforeUnmount(() => {
  window.removeEventListener("auth-changed", syncAuth);
});

// PROCESS: Logout
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  syncAuth();
  router.push({ name: "login" });
}
</script>

<template>
  <div>
    <nav class="navbar navbar-expand navbar-dark bg-dark px-3">
      <span class="navbar-brand fw-bold">HMS</span>

      <div class="navbar-nav me-auto">
        <button
          v-if="isLoggedIn && role === 'admin'"
          class="nav-link btn btn-link"
          @click="$router.push({ name: 'admin' })"
        >
          Admin
        </button>
        <button
          v-if="isLoggedIn && role === 'doctor'"
          class="nav-link btn btn-link"
          @click="$router.push({ name: 'doctor' })"
        >
          Doctor
        </button>
        <button
          v-if="isLoggedIn && role === 'patient'"
          class="nav-link btn btn-link"
          @click="$router.push({ name: 'patient' })"
        >
          Patient
        </button>
      </div>

      <div class="d-flex">
        <!-- Show Login button only when NOT logged in and not already on login page -->
        <button
          v-if="!isLoggedIn && route.name !== 'login'"
          class="btn btn-outline-light btn-sm"
          @click="$router.push({ name: 'login' })"
        >
          Login
        </button>

        <!-- Show Logout only when logged in -->
        <button
          v-if="isLoggedIn"
          class="btn btn-outline-light btn-sm"
          @click="logout"
        >
          Logout
        </button>
      </div>
    </nav>

    <main class="container py-4">
      <router-view />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}
</style>
