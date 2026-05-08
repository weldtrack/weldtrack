<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useLoadingStore } from '../../stores/loading'

const loadingStore = useLoadingStore()
const { isLoading } = storeToRefs(loadingStore)
</script>

<template>
  <Transition name="global-loader-fade">
    <div
      v-if="isLoading"
      class="global-loader"
      role="status"
      aria-live="polite"
      aria-label="Loading"
    >
      <div class="global-loader__card">
        <span class="global-loader__spinner" aria-hidden="true"></span>
        <p class="global-loader__text">Loading...</p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.global-loader {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  background: rgba(8, 15, 26, 0.4);
  backdrop-filter: blur(2px);
}

.global-loader__card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.global-loader__spinner {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  border: 2px solid #93a2b7;
  border-top-color: #0f172a;
  animation: global-loader-spin 0.7s linear infinite;
}

.global-loader__text {
  margin: 0;
  color: #0f172a;
  font-weight: 600;
  font-size: 0.9rem;
}

.global-loader-fade-enter-active,
.global-loader-fade-leave-active {
  transition: opacity 0.18s ease;
}

.global-loader-fade-enter-from,
.global-loader-fade-leave-to {
  opacity: 0;
}

@keyframes global-loader-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>