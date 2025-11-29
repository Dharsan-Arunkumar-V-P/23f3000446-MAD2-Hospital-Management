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

/* ------------------- Splash logic (fancier) ------------------- */
const showSplash = ref(true);
const minDelay = 2000; // milliseconds (change to 3000 for 3s etc.)
/*
  We expose a CSS variable used by animations so the progress bar animation
  is synced with minDelay. Use inline style binding in template.
*/

// Do any async initialization here (token validation, prefetch), if needed.
async function doInit() {
  // Example placeholder - keep minimal if you don't need server checks
  // await validateToken()  <-- place your token validation here
  return Promise.resolve();
}

onMounted(async () => {
  const start = Date.now();
  await doInit();
  const elapsed = Date.now() - start;
  const remaining = Math.max(0, minDelay - elapsed);

  // Keep splash visible at least `remaining` ms, then fade out.
  setTimeout(() => {
    // flip to hide splash (CSS handles the graceful animation)
    showSplash.value = false;
  }, remaining);
});
</script>

<template>
  <div>
    <!-- NAV -->
    <nav class="navbar navbar-expand navbar-dark bg-dark px-3">
      <a class="navbar-brand fw-bold" href="#">
        <img src="/icon-192.png" alt="Medaleon" style="height:28px; margin-right:8px" />
        Medaleon
      </a>

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

    <!-- SPLASH (fancy) -->
    <div
      v-if="showSplash"
      class="splash-root fancy"
      role="img"
      aria-label="Loading Medaleon"
      :style="{ '--splash-duration': minDelay + 'ms' }"
    >
      <div class="splash-card">
        <div class="logo-wrap">
          <div class="orbit"></div>
          <img src="/icon-192.png" alt="Medaleon logo" class="splash-logo" />
        </div>
        <div class="splash-title">Medaleon</div>

        <!-- subtle tagline -->
        <div class="splash-tag">Hospital management, done pretty.</div>

        <!-- progress bar that animates in CSS using --splash-duration -->
        <div class="progress-rail" aria-hidden="true">
          <div class="progress-bar"></div>
        </div>
      </div>
    </div>

    <!-- MAIN APP (hidden / inert while splash visible) -->
    <main :class="{ 'app-hidden': showSplash }" class="container py-4">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
/* base */
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* hide app interactions while splash visible */
.app-hidden {
  pointer-events: none;
  user-select: none;
  -webkit-user-select: none;
  filter: blur(0.2px);
}

/* SPLASH: layout */
.splash-root {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,250,0.98));
  transition: opacity 420ms ease, visibility 420ms ease;
  opacity: 1;
  visibility: visible;
}

/* container card for logo + text */
.splash-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.98);
  border-radius: 14px;
  padding: 18px 22px;
  box-shadow: 0 20px 40px rgba(12,18,26,0.12);
  transform: translateY(0);
  transition: transform 420ms ease, opacity 420ms ease;
}

/* Logo area with orbit ring */
.logo-wrap {
  position: relative;
  width: 110px;
  height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* subtle orbit ring - rotates */
.orbit {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-shadow: 0 6px 20px rgba(11,19,29,0.06) inset;
  pointer-events: none;
  animation: orbit-rotate 1800ms linear infinite;
  opacity: 0.12;
}

/* Logo with pulse and lift */
.splash-logo {
  width: 84px;
  height: 84px;
  object-fit: contain;
  border-radius: 14px;
  background: white;
  padding: 8px;
  box-shadow: 0 8px 28px rgba(11,19,29,0.12);
  transform-origin: center;
  animation: logo-pulse 2000ms ease-in-out infinite;
}

/* Title and tagline */
.splash-title {
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 0.2px;
  color: #0f1720;
}
.splash-tag {
  font-size: 13px;
  color: #6b7280;
  opacity: 0.95;
}

/* Progress rail and animated bar (CSS uses --splash-duration) */
.progress-rail {
  width: 220px;
  height: 6px;
  background: rgba(0,0,0,0.06);
  border-radius: 6px;
  overflow: hidden;
  margin-top: 6px;
}
.progress-bar {
  width: 0%;
  height: 100%;
  background: #e00000;
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.45);
  border-radius: 6px;
  transform-origin: left;
  animation: progress-grow var(--splash-duration) linear forwards;
}

/* keyframes */
@keyframes logo-pulse {
  0% { transform: translateY(0) scale(1); }
  40% { transform: translateY(-6px) scale(1.03); }
  70% { transform: translateY(-3px) scale(1.02); }
  100% { transform: translateY(0) scale(1); }
}
@keyframes orbit-rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes progress-grow {
  0% { width: 6%; opacity: 0.95; }
  20% { width: 28%; }
  60% { width: 70%; }
  100% { width: 100%; opacity: 1; }
}

/* graceful hiding: when showSplash flips false Vue removes element; animation still looks quick */
.splash-root[style*="display: none"] { opacity:0; visibility:hidden; }

/* responsive tweaks */
@media (max-width: 540px) {
  .splash-card { padding: 12px; }
  .logo-wrap { width: 86px; height: 86px; }
  .splash-logo { width: 66px; height: 66px; }
  .progress-rail { width: 170px; }
}
</style>
