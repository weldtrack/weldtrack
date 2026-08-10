<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'

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
        <div class="modal-shell__glow" />

        <div v-if="title || subtitle || closeable" class="modal-shell__header">
          <div>
            <p v-if="subtitle" class="modal-shell__eyebrow">{{ subtitle }}</p>
            <h3 v-if="title" class="modal-shell__title">{{ title }}</h3>
          </div>

          <button
            v-if="closeable"
            type="button"
            class="modal-shell__close"
            aria-label="Close modal"
            @click="emit('close')"
          >
            &times;
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
  padding: 1rem;
}

.modal-shell__backdrop {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.24), transparent 32%),
    radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.16), transparent 28%),
    var(--modal-backdrop, rgba(15, 23, 42, 0.58));
  backdrop-filter: blur(10px);
}

.modal-shell__panel {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  max-height: min(92vh, 58rem);
  overflow: hidden;
  border: 1px solid var(--modal-border, rgba(15, 23, 42, 0.12));
  border-radius: 1.5rem;
  background: var(--modal-surface, linear-gradient(180deg, #ffffff, #f8fafc));
  color: var(--modal-text, #334155);
  box-shadow: var(--modal-shadow, 0 30px 90px rgba(15, 23, 42, 0.28));
}

.modal-shell__glow {
  height: 0.375rem;
  background: linear-gradient(90deg, rgba(59, 130, 246, 1), rgba(14, 165, 233, 0.7));
}

.modal-shell__accent--green .modal-shell__glow {
  background: linear-gradient(90deg, rgba(34, 197, 94, 1), rgba(16, 185, 129, 0.75));
}

.modal-shell__accent--amber .modal-shell__glow {
  background: linear-gradient(90deg, rgba(245, 158, 11, 1), rgba(251, 191, 36, 0.75));
}

.modal-shell__accent--red .modal-shell__glow {
  background: linear-gradient(90deg, rgba(220, 38, 38, 1), rgba(248, 113, 113, 0.8));
}

.modal-shell__accent--slate .modal-shell__glow {
  background: linear-gradient(90deg, rgba(71, 85, 105, 1), rgba(100, 116, 139, 0.8));
}

.modal-shell__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem 0;
}

.modal-shell__eyebrow {
  margin: 0 0 0.25rem;
  color: var(--modal-eyebrow, #64748b);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.modal-shell__title {
  margin: 0;
  color: var(--modal-title, #0f172a);
  font-size: 1.15rem;
  font-weight: 800;
}

.modal-shell__close {
  border: 0;
  border-radius: 9999px;
  background: var(--modal-close-bg, rgba(148, 163, 184, 0.15));
  color: var(--modal-close, #475569);
  font-size: 1.5rem;
  line-height: 1;
  width: 2.25rem;
  height: 2.25rem;
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease;
}

.modal-shell__close:hover {
  background: var(--modal-close-bg-hover, rgba(148, 163, 184, 0.26));
}

.modal-shell__body {
  flex: 1 1 auto;
  min-height: 0;
  padding: 1.25rem 1.5rem 1.5rem;
  overflow-y: auto;
}

.modal-shell__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0 1.5rem 1.5rem;
}

.modal-shell-fade-enter-active,
.modal-shell-fade-leave-active {
  transition: opacity 0.18s ease;
}

.modal-shell-fade-enter-from,
.modal-shell-fade-leave-to {
  opacity: 0;
}

@media (max-width: 479px) {
  .modal-shell {
    align-items: end;
    padding: 0;
  }

  .modal-shell__panel {
    max-height: 94vh;
    border-radius: 1.25rem 1.25rem 0 0;
  }

  .modal-shell__header,
  .modal-shell__body {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .modal-shell__footer {
    flex-direction: column-reverse;
    padding: 0 1rem 1rem;
  }

  .modal-shell__footer :deep(button) {
    width: 100%;
  }
}
</style>
