<script setup lang="ts">
import type { Component } from 'vue'
import { computed, reactive, ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Archive,
  BarChart2,
  Briefcase,
  Calendar,
  ChevronDown,
  ChevronUp,
  ClipboardList,
  Flame,
  Folder,
  LayoutDashboard,
  LogOut,
  MapPin,
  Menu,
  MessageCircle,
  Star,
  Users,
  X,
} from 'lucide-vue-next'
import api from '../../api/api'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{ title: string }>()

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isMobileSidebarOpen = ref(false)
const isLoggingOut = ref(false)
const normalizedRole = computed(() => authStore.role.trim().toLowerCase())
const isSidebarMetaCollapsed = ref(true)

type SidebarLeaf = {
  kind: 'item'
  id: string
  label: string
  icon: Component
  routeName?: string
}

type SidebarGroup = {
  kind: 'group'
  id: string
  label: string
  icon: Component
  children: SidebarLeaf[]
}

type SidebarEntry = SidebarLeaf | SidebarGroup

// Per-role accent so the three portals read as distinct spaces, not one
// reskinned template stamped three times.
const roleAccent = computed(() => {
  if (normalizedRole.value === 'admin') return '#F2A93B' // arc-flash amber
  if (normalizedRole.value === 'staff') return '#4FD1C5' // inspection teal
  if (normalizedRole.value === 'customer') return '#7C9CFF' // signal blue
  return '#F2A93B'
})

const sidebarItems = computed<SidebarEntry[]>(() => {
  if (normalizedRole.value === 'admin') {
    return [
      { kind: 'item', id: 'admin-overview', label: 'Dashboard', icon: LayoutDashboard },
      {
        kind: 'group',
        id: 'admin-group-management',
        label: 'Management',
        icon: Briefcase,
        children: [
          { kind: 'item', id: 'admin-approval', label: 'Booking', icon: Calendar },
          { kind: 'item', id: 'admin-inventory', label: 'Inventory', icon: Archive },
          { kind: 'item', id: 'admin-services', label: 'Services', icon: Briefcase },
        ],
      },
      {
        kind: 'group',
        id: 'admin-group-people',
        label: 'People',
        icon: Users,
        children: [
          { kind: 'item', id: 'admin-staff', label: 'Staff', icon: Users, routeName: 'admin-staff-attendance' },
          { kind: 'item', id: 'admin-users', label: 'Users', icon: Users },
        ],
      },
      { kind: 'item', id: 'admin-reports', label: 'Reports', icon: BarChart2 },
      { kind: 'item', id: 'admin-projects', label: 'Project History', icon: Folder },
      { kind: 'item', id: 'admin-feedback', label: 'Customer Feedback', icon: Star },
    ]
  }

  if (normalizedRole.value === 'staff') {
    return [
      { kind: 'item', id: 'staff-attendance', label: 'Attendance', icon: Calendar },
      { kind: 'item', id: 'staff-tasks', label: 'Tasks', icon: ClipboardList },
      { kind: 'item', id: 'staff-contributions', label: 'Contributions', icon: BarChart2 },
      { kind: 'item', id: 'staff-feedback', label: 'Service Feedback', icon: MessageCircle },
    ]
  }

  if (normalizedRole.value === 'customer') {
    return [
      { kind: 'item', id: 'customer-services', label: 'Services', icon: Briefcase },
      { kind: 'item', id: 'customer-booking', label: 'New Booking', icon: Calendar },
      { kind: 'item', id: 'customer-addresses', label: 'Addresses', icon: MapPin },
      { kind: 'item', id: 'customer-history', label: 'Booking History', icon: Folder },
      { kind: 'item', id: 'customer-feedback', label: 'Service Feedback', icon: MessageCircle },
    ]
  }

  return []
})

const roleLabel = computed(() => {
  if (normalizedRole.value === 'admin') return 'Admin Control Center'
  if (normalizedRole.value === 'staff') return 'Staff Workspace'
  if (normalizedRole.value === 'customer') return 'Customer Portal'
  return 'Workspace'
})

const roleHint = computed(() => {
  if (normalizedRole.value === 'admin') return 'Oversight, approvals, and reporting'
  if (normalizedRole.value === 'staff') return 'Tasks, attendance, and service updates'
  if (normalizedRole.value === 'customer') return 'Bookings, addresses, and feedback'
  return 'Navigation'
})

const getImageUrl = (url?: string) => {
  if (!url) return ''
  // If it's a data URI, return as is
  if (url.startsWith('data:')) return url
  // Otherwise, handle as API path
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

// Groups auto-expand whenever the active route lives inside them, but a
// manual collapse elsewhere is preserved rather than fought.
const openGroups = reactive<Record<string, boolean>>({})

watchEffect(() => {
  for (const entry of sidebarItems.value) {
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
    .then(() => {
      authStore.logout()
      router.replace({ name: 'login' }).catch(() => {})
      isMobileSidebarOpen.value = false
    })
    .catch(() => {
      authStore.logout()
      router.replace({ name: 'login' }).catch(() => {})
      isMobileSidebarOpen.value = false
    })
    .finally(() => {
      isLoggingOut.value = false
    })
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 lg:pl-80" :style="{ '--role-accent': roleAccent }">
    <!-- Top Header -->
    <header
      class="fixed top-0 right-0 z-30 flex h-12.5 w-full items-center justify-between px-6 lg:w-[calc(100%-320px)] lg:justify-end bg-slate-50 border-b border-slate-200">
      <button type="button"
        class="inline-flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 bg-white/90 text-slate-900 shadow-sm backdrop-blur-xl transition hover:bg-white lg:hidden"
        @click="isMobileSidebarOpen = true">
        <Menu class="h-5 w-5" />
      </button>
      <button @click="$router.push({ name: `${authStore.role}-profile` })"
        class="h-8 w-8 overflow-hidden rounded-full border-2 border-transparent bg-slate-200 flex items-center justify-center transition hover:border-[var(--role-accent)]">
        <img v-if="authStore.user?.profile_image" :src="getImageUrl(authStore.user.profile_image)" alt="Profile"
          class="h-full w-full object-cover">
        <span v-else class="text-xs font-semibold text-slate-600">{{ authStore.email?.slice(0, 1).toUpperCase() ||
          'U' }}</span>
      </button>
    </header>

    <div v-if="isMobileSidebarOpen" class="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-[2px] lg:hidden"
      @click="isMobileSidebarOpen = false" />

    <aside
      class="weld-sidebar fixed inset-y-0 left-0 z-50 flex h-screen w-80 flex-col text-white transition-transform duration-200 lg:translate-x-0"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'">

      <!-- Gauge rail: a thin tick strip along the sidebar edge, a nod to a
           pressure gauge, that also encodes which section is live. -->
      <div class="gauge-rail" aria-hidden="true"></div>

      <div class="relative border-b border-white/10 px-5 py-5 lg:px-6">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl border border-[var(--role-accent)]/40 bg-[var(--role-accent)]/10 text-[var(--role-accent)]">
              <Flame class="h-5 w-5" stroke-width="2.25" />
            </div>
            <div>
              <h1 class="brand-mark text-lg leading-tight text-white">WeldTrack</h1>
              <p class="mono-label mt-0.5 text-[10px] text-slate-500">Inventory System</p>
            </div>
          </div>

          <button type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-200 transition hover:bg-white/10 lg:hidden"
            @click="isMobileSidebarOpen = false">
            <X class="h-4 w-4" />
          </button>
        </div>

        <button type="button"
          class="mt-4 inline-flex w-full items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left transition hover:border-white/20 hover:bg-white/[0.06]"
          @click="toggleSidebarMeta">
          <div>
            <p class="mono-label text-slate-500">Workspace Overview</p>
            <p class="mt-1 text-sm font-medium text-white">{{ isSidebarMetaCollapsed ? 'Show info' : 'Hide info' }}</p>
          </div>
          <component :is="isSidebarMetaCollapsed ? ChevronDown : ChevronUp" class="h-4 w-4 text-slate-400" />
        </button>

        <div v-show="!isSidebarMetaCollapsed" class="mt-3 space-y-3">
          <div class="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
            <p class="mono-label text-slate-500">{{ roleLabel }}</p>
            <p class="mt-1 text-sm font-medium text-white">{{ roleHint }}</p>
          </div>
        </div>
      </div>

      <div v-show="!isSidebarMetaCollapsed" class="border-b border-white/10 px-5 py-4 lg:px-6">
        <div class="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3">
          <div
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--role-accent)]/15 text-sm font-semibold text-[var(--role-accent)]">
            {{ authStore.email?.slice(0, 1).toUpperCase() || 'U' }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-white" :title="authStore.email || 'Guest'">
              {{ authStore.email || 'Guest' }}
            </p>
            <p class="truncate text-xs text-slate-500 capitalize">{{ authStore.role || 'customer' }}</p>
          </div>
          <span class="status-dot" aria-hidden="true"></span>
        </div>
      </div>

      <div v-show="!isSidebarMetaCollapsed" class="border-b border-white/10 px-5 py-4 lg:px-6">
        <p class="mono-label text-slate-500">Current Dashboard</p>
        <h2 class="mt-1 text-xl font-semibold tracking-tight text-white">{{ props.title }}</h2>
        <div class="mt-3 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold"
          style="border-color: color-mix(in srgb, var(--role-accent) 35%, transparent); background: color-mix(in srgb, var(--role-accent) 12%, transparent); color: var(--role-accent);">
          <span class="h-1.5 w-1.5 rounded-full" style="background: var(--role-accent);"></span>
          Signed in as <span class="capitalize text-white">{{ authStore.role || 'customer' }}</span>
        </div>
      </div>

      <nav v-if="sidebarItems.length" class="sidebar-nav min-h-0 flex-1 overflow-y-auto px-4 py-4 lg:px-5">
        <div class="mb-3 flex items-center justify-between px-2">
          <p class="mono-label text-slate-500">Navigation</p>
        </div>

        <div class="space-y-1">
          <template v-for="entry in sidebarItems" :key="entry.id">
            <!-- Flat item -->
            <button v-if="entry.kind === 'item'" type="button"
              class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2.5 text-left text-sm font-medium"
              :class="isEntryActive(entry) ? 'nav-row--active' : ''"
              @click="selectSection(entry)">
              <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition"
                :class="isEntryActive(entry)
                  ? 'border-transparent bg-white text-slate-950'
                  : 'border-white/10 bg-white/[0.03] text-slate-400 group-hover:border-white/20 group-hover:text-white'">
                <component :is="entry.icon" class="h-4 w-4" />
              </span>
              <span class="min-w-0 flex-1 truncate">{{ entry.label }}</span>
            </button>

            <!-- Group with children -->
            <div v-else class="nav-group">
              <button type="button"
                class="nav-row group flex w-full items-center gap-3 rounded-lg px-3.5 py-2.5 text-left text-sm font-medium"
                :class="isEntryActive(entry) && !isGroupOpen(entry) ? 'nav-row--active' : ''"
                @click="toggleGroup(entry)">
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition"
                  :class="isEntryActive(entry)
                    ? 'border-[var(--role-accent)]/40 bg-[var(--role-accent)]/10 text-[var(--role-accent)]'
                    : 'border-white/10 bg-white/[0.03] text-slate-400 group-hover:border-white/20 group-hover:text-white'">
                  <component :is="entry.icon" class="h-4 w-4" />
                </span>
                <span class="min-w-0 flex-1 truncate">{{ entry.label }}</span>
                <span class="mono-label !text-[10px] text-slate-600">{{ entry.children.length }}</span>
                <ChevronDown class="h-3.5 w-3.5 shrink-0 text-slate-500 transition-transform duration-200"
                  :class="isGroupOpen(entry) ? 'rotate-180' : ''" />
              </button>

              <div class="nav-subgroup" :class="isGroupOpen(entry) ? 'nav-subgroup--open' : ''">
                <div class="nav-subgroup-inner">
                  <button v-for="child in entry.children" :key="child.id" type="button"
                    class="nav-row nav-row--child group flex w-full items-center gap-3 rounded-lg py-2 pl-3.5 pr-3 text-left text-[13px] font-medium"
                    :class="isEntryActive(child) ? 'nav-row--active' : ''"
                    @click="selectSection(child)">
                    <span class="child-tick" :class="isEntryActive(child) ? 'child-tick--active' : ''"
                      aria-hidden="true"></span>
                    <component :is="child.icon" class="h-3.5 w-3.5 shrink-0"
                      :class="isEntryActive(child) ? 'text-slate-950' : 'text-slate-500'" />
                    <span class="min-w-0 flex-1 truncate">{{ child.label }}</span>
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </nav>

      <div class="relative border-t border-white/10 px-5 py-5 lg:px-6 lg:pb-6">
        <button type="button"
          class="flex w-full items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-rose-400/30 hover:bg-rose-500/10 hover:text-rose-100 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isLoggingOut" @click="handleLogout">
          <LogOut class="h-4 w-4" />
          {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
        </button>
      </div>
    </aside>

    <div class="flex-1 lg:h-screen lg:overflow-y-auto">
      <section class="p-4 pt-16.5 sm:p-6 sm:pt-18.5 lg:p-8 lg:pt-16.5">
        <slot />
      </section>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=JetBrains+Mono:wght@500&display=swap');

.weld-sidebar {
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(255, 255, 255, 0.04) 0%, transparent 45%),
    linear-gradient(180deg, #12161c 0%, #0f1216 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 24px 0 60px rgba(2, 6, 23, 0.35);
  padding-left: 3px;
}

/* Signature element: a pressure-gauge-style tick rail down the sidebar's
   left edge, echoing an instrument gauge rather than a generic accent bar. */
.gauge-rail {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background:
    repeating-linear-gradient(180deg,
      color-mix(in srgb, var(--role-accent) 55%, transparent) 0px,
      color-mix(in srgb, var(--role-accent) 55%, transparent) 2px,
      transparent 2px,
      transparent 14px);
  opacity: 0.55;
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
}

.status-dot {
  height: 8px;
  width: 8px;
  border-radius: 9999px;
  background: var(--role-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--role-accent) 20%, transparent);
}

.nav-row {
  color: rgb(203 213 225);
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-row:hover {
  background: rgba(255, 255, 255, 0.045);
  color: white;
}

.nav-row:focus-visible {
  outline: 2px solid var(--role-accent);
  outline-offset: 2px;
}

.nav-row--active {
  background: white;
  color: rgb(2 6 23);
}

.nav-row--active:hover {
  background: white;
  color: rgb(2 6 23);
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
  border-left: 1px dashed rgba(255, 255, 255, 0.12);
  margin-left: 1.15rem;
}

.nav-subgroup-inner>* + * {
  margin-top: 1px;
}

.child-tick {
  height: 4px;
  width: 4px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.25);
  flex-shrink: 0;
}

.child-tick--active {
  background: rgb(2 6 23);
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