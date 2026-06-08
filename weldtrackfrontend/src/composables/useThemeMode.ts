import { computed, ref } from 'vue'

const THEME_STORAGE_KEY = 'weldtrack-public-theme'
type ThemeMode = 'dark' | 'light'

const storedTheme =
  typeof window !== 'undefined'
    ? (window.localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null)
    : null

const themeMode = ref<ThemeMode>(storedTheme === 'light' ? 'light' : 'dark')

function persistTheme() {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(THEME_STORAGE_KEY, themeMode.value)
}

export function useThemeMode() {
  const isDarkMode = computed(() => themeMode.value === 'dark')

  function toggleTheme() {
    themeMode.value = isDarkMode.value ? 'light' : 'dark'
    persistTheme()
  }

  return {
    isDarkMode,
    themeMode,
    toggleTheme,
  }
}
