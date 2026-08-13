<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronDown,
  LogOut,
  Menu,
  X,
} from 'lucide-vue-next'
import api from '../../../api/api'
import { useThemeMode } from '../../../composables/useThemeMode'
import { useAuthStore } from '../../../stores/auth'
import ThemeToggle from '../../../components/ui/ThemeToggle.vue'
import NotificationDropdown from '../components/shared/NotificationDropdown.vue'
import { resolveImageUrl } from '../../../services/images'

export type SidebarLeaf = {
  kind: 'item'
  id: string
  label: string
  icon: Component
  routeName?: string
}

export type SidebarGroup = {
  kind: 'group'
  id: string
  label: string
  icon: Component
  children: SidebarLeaf[]
}

export type SidebarEntry = SidebarLeaf | SidebarGroup
export type DashboardRole = 'admin' | 'staff' | 'customer'

const props = defineProps<{
  title: string
  role: DashboardRole
  roleLabel: string
  roleHint: string
  accent: string
  navigation: SidebarEntry[]
}>()

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isDarkMode } = useThemeMode()

const isMobileSidebarOpen = ref(false)
const isLoggingOut = ref(false)
const openGroups = reactive<Record<string, boolean>>({})

function closeMobileSidebar() {
  isMobileSidebarOpen.value = false
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') closeMobileSidebar()
}

onMounted(() => window.addEventListener('keydown', handleEscape))
onBeforeUnmount(() => window.removeEventListener('keydown', handleEscape))
watch(() => route.fullPath, closeMobileSidebar)

const currentDateLabel = computed(() =>
  new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date()),
)

const dashboardThemeClass = computed(() => (isDarkMode.value ? 'dashboard-dark' : 'dashboard-light'))

const getImageUrl = resolveImageUrl

function isEntryActive(entry: SidebarEntry): boolean {
  const current = String(route.name ?? '')
  if (entry.kind === 'item') {
    return current.startsWith(entry.id)
  }
  return entry.children.some((child) => current.startsWith(child.id))
}

watchEffect(() => {
  for (const entry of props.navigation) {
    if (entry.kind === 'group' && isEntryActive(entry)) {
      openGroups[entry.id] = true
    }
  }
})

function isGroupOpen(group: SidebarGroup) {
  return !!openGroups[group.id]
}

function toggleGroup(group: SidebarGroup) {
  openGroups[group.id] = !openGroups[group.id]
}

function selectSection(entry: SidebarLeaf) {
  const target = entry.routeName ?? entry.id
  router.push({ name: target }).catch(() => {})
  isMobileSidebarOpen.value = false
}

function handleLogout() {
  isLoggingOut.value = true

  api
    .post('/auth/logout')
    .finally(() => {
      authStore.logout()
      router.replace({ name: 'login' }).catch(() => {})
      isMobileSidebarOpen.value = false
      isLoggingOut.value = false
    })
}
</script>

<template>
  <div
    :class="['dashboard-theme-page min-h-screen overflow-x-hidden lg:pl-80', dashboardThemeClass]"
    :style="{ '--role-accent': props.accent }"
  >
    <header class="dashboard-header fixed top-0 right-0 z-30 flex h-[3.25rem] w-full items-center justify-between px-4 sm:px-6 lg:w-[calc(100%-320px)]">
      <button
        type="button"
        class="dashboard-icon-btn inline-flex lg:hidden"
        aria-label="Open navigation"
        :aria-expanded="isMobileSidebarOpen"
        aria-controls="dashboard-navigation"
        @click="isMobileSidebarOpen = true"
      >
        <Menu class="h-5 w-5" />
      </button>

      <div class="ml-2 hidden min-w-0 lg:block">
        <p class="dashboard-eyebrow">{{ props.roleLabel }}</p>
        <h1 class="truncate text-sm font-semibold">{{ props.title }}</h1>
      </div>

      <div class="ml-auto flex items-center gap-2 sm:gap-3">
        <div class="hidden rounded-full border px-3 py-0.5 text-[11px] font-medium sm:block dashboard-soft-pill">
          {{ currentDateLabel }}
        </div>
        <ThemeToggle />
        <NotificationDropdown />
        <button
          type="button"
          class="dashboard-avatar-btn"
          aria-label="Open profile"
          @click="$router.push({ name: `${props.role}-profile` })"
        >
          <img
            v-if="authStore.user?.profile_image"
            :src="getImageUrl(authStore.user.profile_image)"
            alt="Profile"
            class="h-full w-full object-cover"
          >
          <span v-else class="text-xs font-semibold">{{ authStore.email?.slice(0, 1).toUpperCase() || 'U' }}</span>
        </button>
      </div>
    </header>

    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-[2px] lg:hidden"
      @click="isMobileSidebarOpen = false"
    />

    <aside
      id="dashboard-navigation"
      class="dashboard-sidebar fixed inset-y-0 left-0 z-50 flex h-screen w-[75vw] max-w-[320px] sm:w-80 flex-col transition-transform duration-200 lg:translate-x-0"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="gauge-rail" aria-hidden="true"></div>

      <div class="border-b px-5 py-5 lg:px-6 dashboard-border-soft">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <img src="/weldtrack.png" alt="WeldTrack Logo" class="h-10 w-auto shrink-0 object-contain" />
            <div>
              <h2 class="brand-mark text-lg leading-tight">WeldTrack</h2>
              <p class="mono-label mt-0.5 text-[10px]">Operations Console</p>
            </div>
          </div>

          <button
            type="button"
            class="dashboard-icon-btn inline-flex lg:hidden"
            aria-label="Close navigation"
            @click="isMobileSidebarOpen = false"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

      </div>

      <nav class="sidebar-nav min-h-0 flex-1 overflow-y-auto px-4 py-4 lg:px-5">
        <div class="mb-3 flex items-center justify-between px-2">
          <p class="mono-label">Navigation</p>
        </div>

        <div class="space-y-1">
          <template v-for="entry in props.navigation" :key="entry.id">
            <button
              v-if="entry.kind === 'item'"
              type="button"
              class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2 text-left text-sm font-medium"
              :class="isEntryActive(entry) ? 'nav-row--active' : ''"
              @click="selectSection(entry)"
            >
              <span class="dashboard-icon-wrap" :class="isEntryActive(entry) ? 'dashboard-icon-wrap--active' : ''">
                <component :is="entry.icon" class="h-4 w-4" />
              </span>
              <span class="min-w-0 flex-1 truncate">{{ entry.label }}</span>
            </button>

            <div v-else class="nav-group">
              <button
                type="button"
                class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2 text-left text-sm font-medium"
                :class="isEntryActive(entry) && !isGroupOpen(entry) ? 'nav-row--active' : ''"
                :aria-expanded="isGroupOpen(entry)"
                @click="toggleGroup(entry)"
              >
                <span class="dashboard-icon-wrap" :class="isEntryActive(entry) ? 'dashboard-icon-wrap--active' : ''">
                  <component :is="entry.icon" class="h-4 w-4" />
                </span>
                <span class="min-w-0 flex-1 truncate">{{ entry.label }}</span>
                <span class="mono-label !text-[10px]">{{ entry.children.length }}</span>
                <ChevronDown class="h-3.5 w-3.5 shrink-0 transition-transform duration-200" :class="isGroupOpen(entry) ? 'rotate-180' : ''" />
              </button>

              <div class="nav-subgroup" :class="isGroupOpen(entry) ? 'nav-subgroup--open' : ''">
                <div class="nav-subgroup-inner">
                  <button
                    v-for="child in entry.children"
                    :key="child.id"
                    type="button"
                    class="nav-row nav-row--child group flex w-full items-center gap-3 rounded-lg py-2 pl-3.5 pr-3 text-left text-[13px] font-medium"
                    :class="isEntryActive(child) ? 'nav-row--active' : ''"
                    @click="selectSection(child)"
                  >
                    <span class="child-tick" :class="isEntryActive(child) ? 'child-tick--active' : ''" aria-hidden="true"></span>
                    <component :is="child.icon" class="h-3.5 w-3.5 shrink-0" />
                    <span class="min-w-0 flex-1 truncate">{{ child.label }}</span>
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </nav>

      <div class="border-t px-5 py-5 lg:px-6 dashboard-border-soft">
        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-semibold transition dashboard-ghost-btn"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          <LogOut class="h-4 w-4" />
          {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
        </button>
      </div>
    </aside>

    <div class="flex-1 lg:h-screen lg:overflow-y-auto">
      <section class="p-4 pt-18 sm:p-6 sm:pt-20 lg:p-8 lg:pt-18">
        <slot />
      </section>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');

.dashboard-theme-page {
  font-family: 'Inter', sans-serif;
  --db-bg: #fafafa;
  --db-text: #09090b;
  --db-muted: #71717a;
  --db-border: #e4e4e7;
  --db-sidebar: #ffffff;
  --db-sidebar-text: #52525b;
  --db-panel: #ffffff;
  --db-panel-solid: #ffffff;
  --db-header: rgba(250, 250, 250, 0.85);
  --db-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --db-shadow-lg: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  --db-hover: #f4f4f5;
  background: var(--db-bg);
  color: var(--db-text);
}

.dashboard-theme-page.dashboard-dark {
  --db-bg: #0f172a;
  --db-text: #f8fafc;
  --db-muted: #94a3b8;
  --db-border: #1e293b;
  --db-sidebar: #0f172a;
  --db-sidebar-text: #cbd5e1;
  --db-panel: #0f172a;
  --db-panel-solid: #1e293b;
  --db-header: rgba(15, 23, 42, 0.85);
  --db-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
  --db-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.5);
  --db-hover: #1e293b;
}

.dashboard-header {
  border-bottom: 1px solid var(--db-border);
  background: var(--db-header);
  color: var(--db-text);
  backdrop-filter: blur(12px);
}

.dashboard-sidebar {
  background: var(--db-sidebar);
  color: var(--db-sidebar-text);
  border-right: 1px solid var(--db-border);
}

.dashboard-border-soft {
  border-color: var(--db-border);
}

.dashboard-panel {
  background: var(--db-panel-solid);
  border: 1px solid var(--db-border);
  box-shadow: var(--db-shadow);
}

.dashboard-soft-pill {
  border-color: var(--db-border);
  background: var(--db-panel-solid);
  color: var(--db-muted);
}

.dashboard-theme-page :deep(.theme-toggle) {
  border: 1px solid var(--db-border);
  background: var(--db-panel-solid);
  color: var(--db-muted);
  box-shadow: var(--db-shadow);
  transition: all 0.2s ease;
}

.dashboard-theme-page :deep(.theme-toggle:hover) {
  background: var(--db-hover);
  color: var(--db-text);
}

.dashboard-icon-btn {
  height: 2.25rem;
  width: 2.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  border: 1px solid var(--db-border);
  background: var(--db-panel-solid);
  color: var(--db-muted);
  box-shadow: var(--db-shadow);
  transition: all 0.2s ease;
}

.dashboard-icon-btn:hover {
  background: var(--db-hover);
  color: var(--db-text);
}

.dashboard-avatar-btn {
  height: 2.25rem;
  width: 2.25rem;
  overflow: hidden;
  border-radius: 9999px;
  border: 1px solid var(--db-border);
  background: var(--db-panel-solid);
  box-shadow: var(--db-shadow);
  transition: all 0.2s ease;
}

.dashboard-avatar-btn:hover {
  border-color: var(--db-muted);
}

.dashboard-brand-icon {
  display: flex;
  height: 2.25rem;
  width: 2.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: var(--db-text);
  color: var(--db-bg);
  transition: opacity 0.2s ease;
}

.dashboard-brand-icon:hover {
  opacity: 0.9;
}

.dashboard-initial {
  display: flex;
  height: 2.25rem;
  width: 2.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: var(--db-hover);
  color: var(--db-text);
  font-size: 0.875rem;
  font-weight: 600;
  border: 1px solid var(--db-border);
}

.dashboard-eyebrow {
  color: var(--db-muted);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.dashboard-ghost-btn {
  border-color: var(--db-border);
  background: transparent;
  color: var(--db-text);
}

.dashboard-ghost-btn:hover {
  background: var(--db-hover);
}

.brand-mark {
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--db-text);
}

.mono-label {
  font-family: 'Inter', sans-serif;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--db-muted);
}

.gauge-rail {
  display: none; /* Removed for a cleaner look */
}

.status-dot {
  height: 8px;
  width: 8px;
  border-radius: 9999px;
  background: #10b981;
}

.nav-row {
  color: var(--db-sidebar-text);
  transition: all 0.15s ease;
}

.nav-row:hover {
  background: var(--db-hover);
  color: var(--db-text);
}

.nav-row:focus-visible {
  outline: 2px solid var(--db-border);
  outline-offset: 2px;
}

.dashboard-theme-page .nav-row--active {
  background: var(--db-hover);
  color: var(--db-text);
  font-weight: 600;
}

.dashboard-icon-wrap {
  display: flex;
  height: 1.25rem;
  width: 1.25rem;
  align-items: center;
  justify-content: center;
  color: var(--db-muted);
  transition: color 0.15s ease;
}

.dashboard-theme-page .nav-row:hover .dashboard-icon-wrap,
.dashboard-theme-page .nav-row--active .dashboard-icon-wrap {
  color: var(--db-text);
}

.nav-subgroup {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.2s ease;
}

.nav-subgroup--open {
  grid-template-rows: 1fr;
}

.nav-subgroup-inner {
  overflow: hidden;
  padding-left: 1.5rem;
  margin-top: 2px;
}

.nav-subgroup-inner > * + * {
  margin-top: 2px;
}

.child-tick {
  display: none; /* Removed for a cleaner look */
}

.sidebar-nav {
  scrollbar-width: thin;
  scrollbar-color: var(--db-border) transparent;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: var(--db-border);
  border-radius: 9999px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background-color: var(--db-muted);
}

@media (prefers-reduced-motion: reduce) {
  .nav-subgroup {
    transition: none;
  }
}
</style>
