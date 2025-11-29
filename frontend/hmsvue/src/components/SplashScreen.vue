<template>
  <div class="splash-root" :class="{ 'is-hidden': hidden }" role="img" aria-label="Loading">
    <div class="splash-inner">
      <img :src="logoSrc" alt="Logo" class="splash-logo" />
      <div class="splash-text">Medaleon</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
const logoSrc = "/icon-192.png";

const hidden = ref(false);

/* parent controls hiding; this component can also self-hide if needed */
export function hideSplash() {
  hidden.value = true;
}
</script>

<style scoped>
.splash-root {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 10% 10%, rgba(0,0,0,0.04), rgba(255,255,255,1));
  z-index: 99999;
  transition: opacity .45s ease, visibility .45s;
  opacity: 1;
  visibility: visible;
}

.splash-root.is-hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.splash-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transform: translateY(0);
  transition: transform .45s ease;
}

.splash-root.is-hidden .splash-inner {
  transform: translateY(-6px);
}

/* Logo */
.splash-logo {
  width: 88px;
  height: 88px;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(11,19,29,0.12);
  background: white;
  padding: 8px;
}

/* Small brand text */
.splash-text {
  font-weight: 700;
  font-size: 18px;
  color: #111827;
  letter-spacing: 0.2px;
  opacity: 0.95;
}
</style>
