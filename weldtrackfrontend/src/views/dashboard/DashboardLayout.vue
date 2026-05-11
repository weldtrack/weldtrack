<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useAdminSectionStore, type AdminSection } from '../../stores/adminSection'

const props = defineProps<{ title: string }>()

const authStore = useAuthStore()
const adminSectionStore = useAdminSectionStore()
const router = useRouter()
const isMobileSidebarOpen = ref(false)
const isLoggingOut = ref(false)
const normalizedRole = computed(() => authStore.role.trim().toLowerCase())

const sidebarItems = computed<Array<{ id: AdminSection; label: string }>>(() => {
  if (normalizedRole.value === 'admin') {
    return [
      { id: 'dashboard', label: 'Dashboard' },
      { id: 'booking', label: 'Booking' },
      { id: 'inventory', label: 'Inventory' },
      { id: 'staff', label: 'Staff' },
      { id: 'users', label: 'Users' },
      { id: 'reports', label: 'Reports' },
      { id: 'projects', label: 'Project History' },
      { id: 'feedback', label: 'Customer Feedback' },
    ]
  }

  if (normalizedRole.value === 'staff') {
    return [
      { id: 'staff-attendance', label: 'Attendance' },
      { id: 'staff-tasks', label: 'Tasks' },
      { id: 'staff-contributions', label: 'Contributions' },
      { id: 'staff-feedback', label: 'Service Feedback' },
    ]
  }

  if (normalizedRole.value === 'customer') {
    return [
      { id: 'booking', label: 'New Booking' },
      { id: 'addresses', label: 'Addresses' },
      { id: 'booking-history', label: 'Booking History' },
      { id: 'feedback', label: 'Service Feedback' },
    ]
  }

  return []
})

onMounted(() => {
  if (normalizedRole.value === 'admin' && adminSectionStore.section !== 'dashboard') {
    adminSectionStore.setSection('dashboard')
  }

  if (normalizedRole.value === 'customer' && !['booking', 'addresses', 'booking-history', 'feedback'].includes(adminSectionStore.section)) {
    adminSectionStore.setSection('booking')
  }

  if (normalizedRole.value === 'staff' && !adminSectionStore.section.startsWith('staff')) {
    adminSectionStore.setSection('staff-attendance')
  }
})

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
  <div class="min-h-screen bg-gray-50 lg:pl-72">
    <button
      type="button"
      class="fixed left-4 top-4 z-40 inline-flex items-center justify-center rounded-lg bg-slate-800 p-2 text-white shadow-lg lg:hidden"
      @click="isMobileSidebarOpen = true"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 z-40 bg-black/50 lg:hidden"
      @click="isMobileSidebarOpen = false"
    />

    <aside
      class="fixed inset-y-0 left-0 z-50 flex h-screen w-72 flex-col border-r border-slate-700 bg-slate-800 pb-6 text-white transition-transform duration-200 lg:translate-x-0"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex items-center justify-between gap-4 border-b border-slate-700 px-5 py-4 lg:px-6 lg:py-6">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-white">WeldTrack</h1>
            <p class="text-xs text-slate-400">Inventory System</p>
          </div>
        </div>

        <button
          type="button"
          class="rounded-lg bg-slate-700 p-2 text-slate-200 lg:hidden"
          @click="isMobileSidebarOpen = false"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="border-b border-slate-700 px-5 py-4 lg:px-6">
        <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Current Dashboard</p>
        <h2 class="mt-1 text-xl font-semibold text-white">{{ props.title }}</h2>
        <p class="mt-2 text-sm text-slate-300">
          Signed in as <span class="font-medium capitalize text-white">{{ authStore.role || 'customer' }}</span>
        </p>
      </div>

      <nav v-if="sidebarItems.length" class="sidebar-nav min-h-0 flex-1 overflow-y-auto px-3 py-4 lg:px-4">
        <p class="px-3 pb-2 text-xs uppercase tracking-[0.2em] text-slate-400">Navigation</p>
        <div class="space-y-1">
          <button
            v-for="item in sidebarItems"
            :key="item.id"
            type="button"
            class="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition-colors"
            :class="adminSectionStore.section === item.id ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700 hover:text-white'"
            @click="selectSection(item.id)"
          >
            <span class="h-2 w-2 rounded-full bg-current opacity-70"></span>
            {{ item.label }}
          </button>
        </div>
      </nav>

      <div class="border-t border-slate-700 px-5 py-4 lg:px-6 lg:pb-6">
        <div class="mb-3 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-700 text-slate-200">
            {{ authStore.email?.slice(0, 1).toUpperCase() || 'U' }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-white">{{ authStore.email || 'Guest' }}</p>
            <p class="truncate text-xs text-slate-400 capitalize">{{ authStore.role || 'customer' }}</p>
          </div>
        </div>

        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-700 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
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
  scrollbar-color: #334155 #1e293b;
}

.sidebar-nav::-webkit-scrollbar {
  width: 8px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: #1e293b;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: #334155;
  border-radius: 9999px;
  border: 2px solid #1e293b;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background-color: #475569;
}
</style>
