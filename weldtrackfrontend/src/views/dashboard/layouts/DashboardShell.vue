<script setup lang="ts">
import type { Component } from 'vue'
import { computed, reactive, ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronDown,
  ChevronUp,
  Flame,
  LogOut,
  Menu,
  X,
} from 'lucide-vue-next'
import api from '../../../api/api'
import { useThemeMode } from '../../../composables/useThemeMode'
import { useAuthStore } from '../../../stores/auth'
import ThemeToggle from '../../../components/ui/ThemeToggle.vue'

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
const isSidebarMetaCollapsed = ref(true)
const openGroups = reactive<Record<string, boolean>>({})

const currentDateLabel = computed(() =>
  new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date()),
)

const dashboardThemeClass = computed(() => (isDarkMode.value ? 'dashboard-dark' : 'dashboard-light'))

function getImageUrl(url?: string) {
  if (!url) return ''
  if (url.startsWith('data:')) return url
  const cleanUrl = url.replace('/api', '')
  return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`
}

function toggleSidebarMeta() {
  isSidebarMetaCollapsed.value = !isSidebarMetaCollapsed.value
}

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
    :class="['dashboard-theme-page min-h-screen lg:pl-80', dashboardThemeClass]"
    :style="{ '--role-accent': props.accent }"
  >
    <header class="dashboard-header fixed top-0 right-0 z-30 flex h-14 w-full items-center justify-between px-4 sm:px-6 lg:w-[calc(100%-320px)]">
      <button
        type="button"
        class="dashboard-icon-btn inline-flex lg:hidden"
        @click="isMobileSidebarOpen = true"
      >
        <Menu class="h-5 w-5" />
      </button>

      <div class="ml-2 hidden min-w-0 lg:block">
        <p class="dashboard-eyebrow">{{ props.roleLabel }}</p>
        <h1 class="truncate text-sm font-semibold">{{ props.title }}</h1>
      </div>

      <div class="ml-auto flex items-center gap-2 sm:gap-3">
        <div class="hidden rounded-full border px-3 py-1 text-xs font-medium sm:block dashboard-soft-pill">
          {{ currentDateLabel }}
        </div>
        <ThemeToggle />
        <button
          type="button"
          class="dashboard-avatar-btn"
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
      class="dashboard-sidebar fixed inset-y-0 left-0 z-50 flex h-screen w-80 flex-col transition-transform duration-200 lg:translate-x-0"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="gauge-rail" aria-hidden="true"></div>

      <div class="border-b px-5 py-5 lg:px-6 dashboard-border-soft">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="dashboard-brand-icon">
              <Flame class="h-5 w-5" stroke-width="2.25" />
            </div>
            <div>
              <h2 class="brand-mark text-lg leading-tight">WeldTrack</h2>
              <p class="mono-label mt-0.5 text-[10px]">Operations Console</p>
            </div>
          </div>

          <button
            type="button"
            class="dashboard-icon-btn inline-flex lg:hidden"
            @click="isMobileSidebarOpen = false"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <button
          type="button"
          class="mt-4 inline-flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left transition dashboard-ghost-btn"
          @click="toggleSidebarMeta"
        >
          <div>
            <p class="mono-label">Workspace Overview</p>
            <p class="mt-1 text-sm font-medium">{{ isSidebarMetaCollapsed ? 'Show info' : 'Hide info' }}</p>
          </div>
          <component :is="isSidebarMetaCollapsed ? ChevronDown : ChevronUp" class="h-4 w-4" />
        </button>

        <div v-show="!isSidebarMetaCollapsed" class="mt-3 rounded-xl border px-4 py-3 dashboard-panel dashboard-border-soft">
          <p class="mono-label">{{ props.roleLabel }}</p>
          <p class="mt-1 text-sm font-medium">{{ props.roleHint }}</p>
        </div>
      </div>

      <div v-show="!isSidebarMetaCollapsed" class="border-b px-5 py-4 lg:px-6 dashboard-border-soft">
        <div class="flex items-center gap-3 rounded-xl border px-3 py-3 dashboard-panel dashboard-border-soft">
          <div class="dashboard-initial">
            {{ authStore.email?.slice(0, 1).toUpperCase() || 'U' }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium" :title="authStore.email || 'Guest'">
              {{ authStore.email || 'Guest' }}
            </p>
            <p class="truncate text-xs capitalize">{{ props.role }}</p>
          </div>
          <span class="status-dot" aria-hidden="true"></span>
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
              class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2.5 text-left text-sm font-medium"
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
                class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2.5 text-left text-sm font-medium"
                :class="isEntryActive(entry) && !isGroupOpen(entry) ? 'nav-row--active' : ''"
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
          class="flex w-full items-center justify-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-semibold transition dashboard-ghost-btn"
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
        <div class="dashboard-content-panel rounded-2xl p-4 sm:p-6">
          <slot />
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=JetBrains+Mono:wght@500&display=swap');

.dashboard-theme-page {
  --db-bg: #f8fafc;
  --db-text: #0f172a;
  --db-muted: #475569;
  --db-border: rgba(15, 23, 42, 0.1);
  --db-sidebar: #ffffff;
  --db-sidebar-text: #334155;
  --db-panel: rgba(255, 255, 255, 0.9);
  --db-panel-solid: #ffffff;
  --db-header: rgba(248, 250, 252, 0.92);
  --db-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
  background: var(--db-bg);
  color: var(--db-text);
}

.dashboard-theme-page.dashboard-dark {
  --db-bg: #020617;
  --db-text: #f8fafc;
  --db-muted: #94a3b8;
  --db-border: rgba(255, 255, 255, 0.08);
  --db-sidebar: #0b1220;
  --db-sidebar-text: #cbd5e1;
  --db-panel: rgba(15, 23, 42, 0.72);
  --db-panel-solid: rgba(15, 23, 42, 0.86);
  --db-header: rgba(2, 6, 23, 0.82);
  --db-shadow: 0 24px 60px rgba(2, 6, 23, 0.4);
}

.dashboard-header {
  border-bottom: 1px solid var(--db-border);
  background: var(--db-header);
  color: var(--db-text);
  backdrop-filter: blur(14px);
}

.dashboard-sidebar {
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(255, 255, 255, 0.05) 0%, transparent 45%),
    linear-gradient(180deg, color-mix(in srgb, var(--db-sidebar) 97%, #000) 0%, var(--db-sidebar) 100%);
  color: var(--db-sidebar-text);
  border-right: 1px solid var(--db-border);
  box-shadow: var(--db-shadow);
  padding-left: 3px;
}

.dashboard-content-panel {
  background: var(--db-panel);
  border: 1px solid var(--db-border);
  box-shadow: var(--db-shadow);
}

.dashboard-border-soft {
  border-color: var(--db-border);
}

.dashboard-panel {
  background: color-mix(in srgb, var(--db-panel-solid) 62%, transparent);
}

.dashboard-soft-pill {
  border-color: var(--db-border);
  background: color-mix(in srgb, var(--db-panel-solid) 70%, transparent);
}

.dashboard-theme-page :deep(.theme-toggle) {
  border-color: var(--db-border);
  background: color-mix(in srgb, var(--db-panel-solid) 72%, transparent);
  color: var(--db-text);
}

.dashboard-theme-page :deep(.theme-toggle:hover) {
  background: color-mix(in srgb, var(--db-panel-solid) 96%, transparent);
}

.dashboard-icon-btn {
  height: 2.4rem;
  width: 2.4rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  border: 1px solid var(--db-border);
  background: color-mix(in srgb, var(--db-panel-solid) 74%, transparent);
  transition: background-color 0.16s ease;
}

.dashboard-icon-btn:hover {
  background: color-mix(in srgb, var(--db-panel-solid) 94%, transparent);
}

.dashboard-avatar-btn {
  height: 2.15rem;
  width: 2.15rem;
  overflow: hidden;
  border-radius: 9999px;
  border: 2px solid transparent;
  background: color-mix(in srgb, var(--db-panel-solid) 80%, transparent);
  transition: border-color 0.16s ease;
}

.dashboard-avatar-btn:hover {
  border-color: var(--role-accent);
}

.dashboard-brand-icon {
  display: flex;
  height: 2.75rem;
  width: 2.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  border: 1px solid color-mix(in srgb, var(--role-accent) 35%, transparent);
  background: color-mix(in srgb, var(--role-accent) 14%, transparent);
  color: var(--role-accent);
}

.dashboard-initial {
  display: flex;
  height: 2.75rem;
  width: 2.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--role-accent) 14%, transparent);
  color: var(--role-accent);
  font-size: 0.9rem;
  font-weight: 700;
}

.dashboard-eyebrow {
  color: var(--db-muted);
  font-size: 0.72rem;
}

.dashboard-ghost-btn {
  border-color: var(--db-border);
  background: color-mix(in srgb, var(--db-panel-solid) 45%, transparent);
}

.dashboard-ghost-btn:hover {
  background: color-mix(in srgb, var(--db-panel-solid) 72%, transparent);
}

.brand-mark {
  font-family: 'Oswald', 'Inter', sans-serif;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.mono-label {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--db-muted) 88%, #fff 12%);
}

.gauge-rail {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background:
    repeating-linear-gradient(180deg,
      color-mix(in srgb, var(--role-accent) 58%, transparent) 0px,
      color-mix(in srgb, var(--role-accent) 58%, transparent) 2px,
      transparent 2px,
      transparent 14px);
  opacity: 0.6;
}

.status-dot {
  height: 8px;
  width: 8px;
  border-radius: 9999px;
  background: var(--role-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--role-accent) 20%, transparent);
}

.nav-row {
  color: var(--db-sidebar-text);
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.dashboard-theme-page.dashboard-light .nav-row:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.dashboard-theme-page.dashboard-light .dashboard-icon-wrap {
  background: #f8fafc;
  color: #475569;
}

.dashboard-theme-page.dashboard-light .dashboard-icon-wrap--active {
  border-color: color-mix(in srgb, var(--role-accent) 45%, #cbd5e1);
  background: color-mix(in srgb, var(--role-accent) 14%, white);
  color: color-mix(in srgb, var(--role-accent) 78%, #0f172a);
}

.nav-row:focus-visible {
  outline: 2px solid var(--role-accent);
  outline-offset: 2px;
}

.dashboard-theme-page.dashboard-light .nav-row--active {
  background: color-mix(in srgb, var(--role-accent) 13%, white);
  color: #0f172a;
}

.dashboard-theme-page.dashboard-dark .nav-row--active {
  background: color-mix(in srgb, var(--role-accent) 16%, transparent);
  color: var(--db-text);
}

.dashboard-icon-wrap {
  display: flex;
  height: 2rem;
  width: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.6rem;
  border: 1px solid color-mix(in srgb, var(--db-border) 88%, transparent);
  background: rgba(255, 255, 255, 0.04);
  color: color-mix(in srgb, var(--db-sidebar-text) 85%, #fff 15%);
}

.dashboard-icon-wrap--active {
  border-color: color-mix(in srgb, var(--role-accent) 40%, transparent);
  background: color-mix(in srgb, var(--role-accent) 16%, transparent);
  color: var(--role-accent);
}

.nav-subgroup {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.22s ease;
}

.nav-subgroup--open {
  grid-template-rows: 1fr;
}

.nav-subgroup-inner {
  overflow: hidden;
  padding-left: 1.35rem;
  margin-top: 2px;
  border-left: 1px dashed color-mix(in srgb, var(--db-border) 92%, transparent);
  margin-left: 1.15rem;
}

.nav-subgroup-inner > * + * {
  margin-top: 1px;
}

.child-tick {
  height: 4px;
  width: 4px;
  border-radius: 9999px;
  background: color-mix(in srgb, var(--db-muted) 70%, transparent);
  flex-shrink: 0;
}

.child-tick--active {
  background: currentColor;
}

.sidebar-nav {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.4) transparent;
}

.sidebar-nav::-webkit-scrollbar {
  width: 8px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.35);
  border-radius: 9999px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background-color: rgba(148, 163, 184, 0.55);
}

@media (prefers-reduced-motion: reduce) {
  .nav-subgroup {
    transition: none;
  }
}
</style>
