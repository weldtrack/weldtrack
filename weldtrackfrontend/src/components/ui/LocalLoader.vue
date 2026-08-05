<template>
  <div class="local-loader" role="status" aria-live="polite" aria-label="Loading">
    <div class="local-loader__card">
      <span class="local-loader__spinner" aria-hidden="true"></span>
      <p class="local-loader__text"><slot>Loading...</slot></p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple presentational loader component for per-component usage
</script>

<style scoped>
.local-loader {
  position: absolute;
  inset: 0;
  z-index: 40;
  display: grid;
  place-items: center;
  /* make overlay fully transparent to avoid white flicker */
  background: transparent;
  color: #0f172a;
}

.local-loader__card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  /* remove card background/border/shadow to keep fully transparent */
  border: 1px solid transparent;
  background: transparent;
  box-shadow: none;
}

.local-loader__spinner {
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 50%;
  border: 2px solid rgba(203, 213, 225, 0.9);
  border-top-color: currentColor;
  color: #0f172a;
  animation: local-loader-spin 0.7s linear infinite;
}

.local-loader__text {
  margin: 0;
  color: currentColor;
  font-weight: 600;
  font-size: 0.9rem;
}

@keyframes local-loader-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-color-scheme: dark) {
  .local-loader {
    background: transparent; /* ensure dark mode is also transparent */
    color: #e6eef8;
  }

  .local-loader__card {
    border: 1px solid transparent;
    background: transparent;
    box-shadow: none;
  }

  .local-loader__spinner {
    border: 2px solid rgba(255, 255, 255, 0.12);
    color: #e6eef8;
    border-top-color: currentColor;
  }

  .local-loader__text {
    color: #e6eef8;
  }
}
</style>