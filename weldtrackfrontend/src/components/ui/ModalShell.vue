<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    show: boolean
    title?: string
    subtitle?: string
    tone?: 'blue' | 'green' | 'amber' | 'red' | 'slate'
    size?: 'sm' | 'md' | 'lg' | 'xl'
    closeable?: boolean
  }>(),
  {
    title: '',
    subtitle: '',
    tone: 'blue',
    size: 'md',
    closeable: true,
  },
)

const emit = defineEmits<{
  close: []
}>()

const sizeClasses = {
  sm: 'w-full max-w-md',
  md: 'w-full max-w-lg',
  lg: 'w-full max-w-2xl',
  xl: 'w-full max-w-4xl',
} as const

const toneClasses = {
  blue: 'modal-shell__accent--blue',
  green: 'modal-shell__accent--green',
  amber: 'modal-shell__accent--amber',
  red: 'modal-shell__accent--red',
  slate: 'modal-shell__accent--slate',
} as const

const dialogLabel = computed(() => props.title || 'Dialog')

let previousBodyOverflow = ''

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.show && props.closeable) emit('close')
}

watch(
  () => props.show,
  (show) => {
    if (show) {
      previousBodyOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', handleKeydown)
    } else {
      document.body.style.overflow = previousBodyOverflow
      window.removeEventListener('keydown', handleKeydown)
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Transition name="modal-shell-fade">
    <div v-if="show" class="modal-shell" role="dialog" aria-modal="true" :aria-label="dialogLabel">
      <div class="modal-shell__backdrop" @click="closeable && emit('close')"></div>

      <div class="modal-shell__panel" :class="[sizeClasses[size], toneClasses[tone]]">
        <div v-if="title || subtitle || closeable" class="modal-shell__header">
          <div class="modal-shell__heading">
            <h3 v-if="title" class="modal-shell__title">{{ title }}</h3>
            <p v-if="subtitle" class="modal-shell__subtitle">{{ subtitle }}</p>
          </div>

          <button
            v-if="closeable"
            type="button"
            class="modal-shell__close"
            aria-label="Close modal"
            @click="emit('close')"
          >
            <X class="modal-shell__close-icon" />
          </button>
        </div>

        <div class="modal-shell__body">
          <slot />
        </div>

        <div v-if="$slots.footer" class="modal-shell__footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-shell {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: grid;
  place-items: center;
  padding: 1.25rem;
}

.modal-shell__backdrop {
  position: absolute;
  inset: 0;
  background: var(--modal-backdrop, rgba(15, 23, 42, 0.58));
  backdrop-filter: blur(6px);
}

.modal-shell__panel {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  max-height: min(92vh, 58rem);
  overflow: hidden;
  border: 1px solid var(--modal-border, rgba(15, 23, 42, 0.12));
  border-radius: 1rem;
  background: var(--modal-surface, #ffffff);
  color: var(--modal-text, #334155);
  box-shadow: var(--modal-shadow, 0 24px 64px rgba(15, 23, 42, 0.24));
}

.modal-shell__accent--blue { --modal-accent: #0284c7; }
.modal-shell__accent--green { --modal-accent: #059669; }
.modal-shell__accent--amber { --modal-accent: #d97706; }
.modal-shell__accent--red { --modal-accent: #dc2626; }
.modal-shell__accent--slate { --modal-accent: #64748b; }

.modal-shell__panel::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--modal-accent, #0284c7);
  content: '';
}

.modal-shell__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--modal-border, rgba(15, 23, 42, 0.1));
}

.modal-shell__heading {
  min-width: 0;
}

.modal-shell__subtitle {
  margin: 0.3rem 0 0;
  color: var(--modal-eyebrow, #64748b);
  font-size: 0.8125rem;
  line-height: 1.35;
}

.modal-shell__title {
  margin: 0;
  color: var(--modal-title, #0f172a);
  font-size: 1.0625rem;
  font-weight: 650;
  letter-spacing: -0.01em;
}

.modal-shell__close {
  border: 0;
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 0.625rem;
  background: transparent;
  color: var(--modal-close, #475569);
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease;
}

.modal-shell__close:hover {
  background: var(--modal-close-bg-hover, rgba(148, 163, 184, 0.26));
}

.modal-shell__close-icon {
  width: 1rem;
  height: 1rem;
}

.modal-shell__body {
  flex: 1 1 auto;
  min-height: 0;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-shell__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--modal-border, rgba(15, 23, 42, 0.1));
}

.modal-shell-fade-enter-active,
.modal-shell-fade-leave-active {
  transition: opacity 0.16s ease;
}

.modal-shell-fade-enter-active .modal-shell__panel,
.modal-shell-fade-leave-active .modal-shell__panel {
  transition: transform 0.16s ease, opacity 0.16s ease;
}

.modal-shell-fade-enter-from,
.modal-shell-fade-leave-to {
  opacity: 0;
}

.modal-shell-fade-enter-from .modal-shell__panel,
.modal-shell-fade-leave-to .modal-shell__panel {
  opacity: 0;
  transform: translateY(0.5rem) scale(0.99);
}

@media (max-width: 479px) {
  .modal-shell {
    align-items: end;
    padding: 0;
  }

  .modal-shell__panel {
    max-height: 94vh;
    border-radius: 1rem 1rem 0 0;
  }

  .modal-shell__header,
  .modal-shell__body {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .modal-shell__footer {
    flex-direction: column-reverse;
    padding: 1rem;
  }

  .modal-shell__footer :deep(button) {
    width: 100%;
  }
}
</style>
