<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Archive,
  BarChart2,
  Briefcase,
  Calendar,
  ClipboardList,
  Folder,
  ChevronDown,
  ChevronUp,
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
import { useAdminSectionStore } from '../../stores/adminSection'
import { type AdminSection } from '../../types/adminSection'

const props = defineProps<{ title: string }>()

const authStore = useAuthStore()
const adminSectionStore = useAdminSectionStore()
const router = useRouter()
const isMobileSidebarOpen = ref(false)
const isLoggingOut = ref(false)
const normalizedRole = computed(() => authStore.role.trim().toLowerCase())
const isSidebarMetaCollapsed = ref(true)

type SidebarItem = {
  id: AdminSection
  label: string
  icon: Component
}

const sidebarItems = computed<SidebarItem[]>(() => {
  if (normalizedRole.value === 'admin') {
    return [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'booking', label: 'Booking', icon: Calendar },
      { id: 'inventory', label: 'Inventory', icon: Archive },
      { id: 'services', label: 'Services', icon: Briefcase },
      { id: 'staff', label: 'Staff', icon: Users },
      { id: 'users', label: 'Users', icon: Users },
      { id: 'reports', label: 'Reports', icon: BarChart2 },
      { id: 'projects', label: 'Project History', icon: Folder },
      { id: 'feedback', label: 'Customer Feedback', icon: Star },
    ]
  }

  if (normalizedRole.value === 'staff') {
    return [
      { id: 'staff-attendance', label: 'Attendance', icon: Calendar },
      { id: 'staff-tasks', label: 'Tasks', icon: ClipboardList },
      { id: 'staff-contributions', label: 'Contributions', icon: BarChart2 },
      { id: 'staff-feedback', label: 'Service Feedback', icon: Star },
    ]
  }

  if (normalizedRole.value === 'customer') {
    return [
      { id: 'services', label: 'Services', icon: Briefcase },
      { id: 'booking', label: 'New Booking', icon: Calendar },
      { id: 'addresses', label: 'Addresses', icon: MapPin },
      { id: 'booking-history', label: 'Booking History', icon: Folder },
      { id: 'feedback', label: 'Service Feedback', icon: MessageCircle },
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

onMounted(() => {
  if (normalizedRole.value === 'admin') {
    const allowedAdminSections = ['dashboard', 'booking', 'inventory', 'services', 'staff', 'users', 'reports', 'projects', 'feedback']
    if (!allowedAdminSections.includes(adminSectionStore.section)) {
      adminSectionStore.setSection('dashboard')
    }
  }

  if (normalizedRole.value === 'customer' && !['services', 'booking', 'addresses', 'booking-history', 'feedback'].includes(adminSectionStore.section)) {
    adminSectionStore.setSection('services')
  }

  if (normalizedRole.value === 'staff' && !adminSectionStore.section.startsWith('staff')) {
    adminSectionStore.setSection('staff-attendance')
  }
})

function toggleSidebarMeta() {
  isSidebarMetaCollapsed.value = !isSidebarMetaCollapsed.value
}

function selectSection(section: AdminSection) {
  if (normalizedRole.value === 'staff' && section === 'staff') {
    router.push({ name: 'staff-dashboard' }).catch(() => {})
    return
  }

  adminSectionStore.setSection(section)
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
  <div class="min-h-screen bg-slate-50 lg:pl-80">
    <button
      type="button"
      class="fixed left-4 top-4 z-40 inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white/90 text-slate-900 shadow-[0_12px_30px_rgba(15,23,42,0.14)] backdrop-blur-xl transition hover:bg-white lg:hidden"
      @click="isMobileSidebarOpen = true"
    >
      <Menu class="h-5 w-5" />
    </button>

    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-[2px] lg:hidden"
      @click="isMobileSidebarOpen = false"
    />

    <aside
      class="fixed inset-y-0 left-0 z-50 flex h-screen w-80 flex-col border-r border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.98)_0%,rgba(15,23,42,0.92)_100%)] text-white shadow-[24px_0_60px_rgba(2,6,23,0.25)] transition-transform duration-200 lg:translate-x-0"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="border-b border-white/10 px-5 py-5 lg:px-6">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#38bdf8_0%,#2563eb_100%)] text-white shadow-[0_12px_25px_rgba(37,99,235,0.32)]">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-semibold tracking-tight text-white">WeldTrack</h1>
              <p class="text-xs text-slate-400">Inventory System</p>
            </div>
          </div>

          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-200 transition hover:bg-white/10 lg:hidden"
            @click="isMobileSidebarOpen = false"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <button
          type="button"
          class="mt-4 inline-flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-left transition hover:bg-white/10"
          @click="toggleSidebarMeta"
        >
          <div>
            <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Workspace Overview</p>
            <p class="mt-1 text-sm font-medium text-white">{{ isSidebarMetaCollapsed ? 'Show info' : 'Hide info' }}</p>
          </div>
          <component :is="isSidebarMetaCollapsed ? ChevronDown : ChevronUp" class="h-4 w-4 text-slate-300" />
        </button>

        <div v-show="!isSidebarMetaCollapsed" class="mt-4 space-y-4">
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-md">
            <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">{{ roleLabel }}</p>
            <p class="mt-1 text-sm font-medium text-white">{{ roleHint }}</p>
          </div>
        </div>
      </div>
      
      <div v-show="!isSidebarMetaCollapsed" class="px-5 py-4 mt-auto">
        <div class="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-3 py-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-sm font-semibold text-white">
              {{ authStore.email?.slice(0, 1).toUpperCase() || 'U' }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-white" :title="authStore.email || 'Guest'">{{ authStore.email || 'Guest' }}</p>
              <p class="truncate text-xs text-slate-400 capitalize">{{ authStore.role || 'customer' }}</p>
            </div>
        </div>
      </div>


      <div v-show="!isSidebarMetaCollapsed" class="border-b border-white/10 px-5 py-4 lg:px-6">
        <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Current Dashboard</p>
        <h2 class="mt-1 text-xl font-semibold tracking-tight text-white">{{ props.title }}</h2>
        <div class="mt-3 inline-flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
          <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
          Signed in as <span class="capitalize text-white">{{ authStore.role || 'customer' }}</span>
        </div>
      </div>


      <nav v-if="sidebarItems.length" class="sidebar-nav min-h-0 flex-1 overflow-y-auto px-4 py-4 lg:px-5">
        <div class="mb-3 flex items-center justify-between px-2">
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Navigation</p>
          <p class="text-[10px] font-medium text-slate-500">{{ sidebarItems.length }} items</p>
        </div>

        <div class="space-y-1.5">
          <button
            v-for="item in sidebarItems"
            :key="item.id"
            type="button"
            class="group flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium transition-all duration-200"
            :class="adminSectionStore.section === item.id
              ? 'bg-white text-slate-950 shadow-[0_10px_30px_rgba(255,255,255,0.08)]'
              : 'text-slate-300 hover:bg-white/6 hover:text-white'"
            @click="selectSection(item.id)"
          >
            <span
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border transition"
              :class="adminSectionStore.section === item.id
                ? 'border-slate-200 bg-slate-100 text-slate-950'
                : 'border-white/10 bg-white/5 text-slate-300 group-hover:border-white/15 group-hover:bg-white/10 group-hover:text-white'"
            >
              <component :is="item.icon" class="h-4 w-4" />
            </span>
            <span class="min-w-0 flex-1 truncate">{{ item.label }}</span>
            <span
              class="h-2 w-2 rounded-full transition"
              :class="adminSectionStore.section === item.id ? 'bg-sky-500' : 'bg-transparent group-hover:bg-slate-500'"
            />
          </button>
        </div>
      </nav>

      <div class="border-t border-white/10 px-5 py-5 lg:px-6 lg:pb-6">
        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-rose-400/20 hover:bg-rose-500/10 hover:text-rose-100 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          <LogOut class="h-4 w-4" />
          {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
        </button>
      </div>
    </aside>

    <div class="flex-1 lg:h-screen lg:overflow-y-auto">
      <section class="p-4 pt-16 sm:p-6 sm:pt-16 lg:p-8 lg:pt-8">
        <slot />
      </section>
    </div>
  </div>
</template>

<style scoped>
.sidebar-nav {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.45) rgba(15, 23, 42, 0.35);
}

.sidebar-nav::-webkit-scrollbar {
  width: 8px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.35);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.4);
  border-radius: 9999px;
  border: 2px solid rgba(15, 23, 42, 0.35);
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background-color: rgba(148, 163, 184, 0.58);
}
</style>
