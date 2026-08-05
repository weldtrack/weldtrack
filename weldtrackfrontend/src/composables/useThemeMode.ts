import { computed, ref, watch } from 'vue'

const THEME_STORAGE_KEY = 'weldtrack-public-theme'
type ThemeMode = 'dark' | 'light'

const storedTheme =
  typeof window !== 'undefined'
    ? (window.localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null)
    : null

const themeMode = ref<ThemeMode>(storedTheme === 'light' ? 'light' : 'dark')

function applyDocumentTheme(mode: ThemeMode) {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.theme = mode
  if (document.body) {
    document.body.style.backgroundColor = mode === 'light' ? '#f8fafc' : '#020617'
    document.body.style.color = mode === 'light' ? '#0f172a' : '#f8fafc'
  }
}

applyDocumentTheme(themeMode.value)
watch(themeMode, applyDocumentTheme)

// Keep every mounted theme toggle in sync, including separate tabs/windows.
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key !== THEME_STORAGE_KEY) return
    themeMode.value = event.newValue === 'light' ? 'light' : 'dark'
  })
}

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
