<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'

defineProps<{
  text: string
}>()
</script>

<template>
  <div class="group relative inline-flex items-center justify-center ml-1.5 cursor-help">
    <AlertCircle class="h-4 w-4 text-slate-400 transition-colors group-hover:text-sky-500 dark:text-slate-500" />
    <div class="pointer-events-none absolute bottom-full left-1/2 z-[99999] mb-2 -translate-x-1/2 opacity-0 transition-opacity group-hover:opacity-100">
      <div class="w-max max-w-xs rounded-lg bg-slate-900 px-3 py-2 text-xs font-medium text-white shadow-lg dark:bg-slate-700">
        {{ text }}
        <svg class="absolute left-1/2 top-full h-2 w-full -translate-x-1/2 text-slate-900 dark:text-slate-700" x="0px" y="0px" viewBox="0 0 255 255" xml:space="preserve"><polygon class="fill-current" points="0,0 127.5,127.5 255,0" /></svg>
      </div>
    </div>
  </div>
</template>
