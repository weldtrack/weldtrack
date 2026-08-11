<script setup lang="ts">
import { storeToRefs } from 'pinia'
import ModalShell from './ModalShell.vue'
import { useModalStore } from '../../stores/modal'

const modalStore = useModalStore()
const { isOpen, title, message, variant, confirmLabel, cancelLabel, showCancel } = storeToRefs(modalStore)

function close() {
  modalStore.close()
}

async function accept() {
  await modalStore.accept()
}

const toneMap = {
  info: 'blue',
  success: 'green',
  warning: 'amber',
  error: 'red',
} as const
</script>

<template>
  <ModalShell :show="isOpen" :title="title" :subtitle="showCancel ? 'Confirm your action' : 'Message'" :tone="toneMap[variant]" size="sm" @close="close">
    <p class="global-modal__message">{{ message }}</p>

    <template #footer>
      <button v-if="showCancel" type="button" class="global-modal__button global-modal__button--secondary" @click="close">
        {{ cancelLabel || 'Cancel' }}
      </button>
      <button type="button" :class="['global-modal__button', variant === 'error' ? 'global-modal__button--danger' : '']" @click="accept">
        {{ confirmLabel }}
      </button>
    </template>
  </ModalShell>
</template>

<style scoped>
.global-modal__message {
  margin: 0;
  color: var(--modal-text, #334155);
  font-size: 0.9375rem;
  line-height: 1.6;
}

.global-modal__button {
  border: 0;
  border-radius: 0.625rem;
  min-height: 2.5rem;
  padding: 0.625rem 1rem;
  background: var(--accent-primary, var(--chart-ongoing, #2563eb));
  color: var(--button-text, #fff);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: filter 150ms ease, transform 150ms ease;
}

.global-modal__button:hover {
  filter: brightness(0.95);
}

.global-modal__button:active {
  transform: scale(0.98);
}

.global-modal__button--secondary {
  background: var(--public-panel-solid, #e2e8f0);
  color: var(--public-text, #0f172a);
}

.global-modal__button--danger {
  background: var(--status-danger, #dc2626);
}
</style>
