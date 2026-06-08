<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { useThemeMode } from '../../composables/useThemeMode'

const { isDarkMode, toggleTheme } = useThemeMode()
</script>

<template>
  <button
    type="button"
    class="theme-toggle inline-flex h-10 w-10 items-center justify-center rounded-full border transition-all active:scale-95"
    :aria-label="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
    :title="isDarkMode ? 'Light mode' : 'Dark mode'"
    @click="toggleTheme"
  >
    <Sun v-if="isDarkMode" class="h-4 w-4" />
    <Moon v-else class="h-4 w-4" />
  </button>
</template>
