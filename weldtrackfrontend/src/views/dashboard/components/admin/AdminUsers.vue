<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Users } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useModalStore } from '../../../../stores/modal'

type User = {
  id: number
  email: string
  role: string
  created_at: string
  is_banned: boolean
  is_online?: boolean
  last_active?: string | null
}

const users = ref<User[]>([])
const view = ref<'all' | 'online'>('all')
const roleFilter = ref<'all' | 'customers' | 'staff'>('all')
const search = ref('')
const loading = ref(false)
const refreshInterval = ref<number | null>(null)
const modalStore = useModalStore()

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/auth/admin/users', { skipGlobalLoading: true } as any)
    users.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function fetchOnline() {
  loading.value = true
  try {
    const res = await api.get('/auth/admin/online', { skipGlobalLoading: true } as any)
    users.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function refresh() {
  if (view.value === 'online') await fetchOnline()
  else await fetchUsers()
}

function banUser(id: number) {
  modalStore.open({
    title: 'Confirm Ban',
    message: 'Are you sure you want to ban this user?',
    variant: 'error',
    confirmLabel: 'Ban',
    cancelLabel: 'Cancel',
    onConfirm: async () => {
      loading.value = true
      try {
        await api.post(`/auth/admin/ban/${id}`, {}, { skipGlobalLoading: true } as any)
        await refresh()
      } catch (e) {
      } finally {
        loading.value = false
      }
    },
  })
}

function unbanUser(id: number) {
  modalStore.open({
    title: 'Confirm Unban',
    message: 'Are you sure you want to unban this user?',
    variant: 'warning',
    confirmLabel: 'Unban',
    cancelLabel: 'Cancel',
    onConfirm: async () => {
      loading.value = true
      try {
        await api.post(`/auth/admin/unban/${id}`, {}, { skipGlobalLoading: true } as any)
        await refresh()
      } catch (e) {
      } finally {
        loading.value = false
      }
    },
  })
}

function isOnline(user: User) {
  return Boolean(user.is_online)
}

const filtered = computed(() => {
  const term = search.value.trim().toLowerCase()
  return users.value
    .filter((u) => u.role.toLowerCase() !== 'admin')
    .filter((u) => {
      if (roleFilter.value === 'customers') return u.role.toLowerCase() === 'customer'
      if (roleFilter.value === 'staff') return u.role.toLowerCase() === 'staff'
      return true
    })
    .filter((u) => {
      if (!term) return true
      return (
        u.email.toLowerCase().includes(term) ||
        u.role.toLowerCase().includes(term) ||
        String(u.id).includes(term)
      )
    })
})

onMounted(() => {
  refresh()
  refreshInterval.value = window.setInterval(() => {
    refresh()
  }, 5000)
})

onBeforeUnmount(() => {
  if (refreshInterval.value !== null) {
    window.clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
})
</script>

<template>
  <div class="overflow-hidden rounded-lg border border-gray-200 bg-white p-4 sm:p-6 relative">
    <LocalLoader v-if="loading" />
    <div class="mb-4">
      <div class="mb-4 flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-blue-50 to-white ring-1 ring-blue-100">
          <Users class="h-5 w-5 text-blue-600" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900">Users</h3>
          <p class="mt-0.5 text-sm text-gray-500">Manage customer and staff accounts</p>
        </div>
      </div>
      <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-2">
        <input v-model="search" placeholder="Search users..." class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-slate-900 sm:flex-1" />

        <div class="w-32 sm:w-40">
          <div class="relative">
            <select
              v-model="roleFilter"
              class="h-10 w-full appearance-none truncate rounded-md border border-gray-300 bg-white px-2 pr-8 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            >
              <option value="all">All</option>
              <option value="customers">Customers</option>
              <option value="staff">Staff</option>
            </select>
            <span class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-500">
              <svg viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4" aria-hidden="true">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.51a.75.75 0 01-1.08 0l-4.25-4.51a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
              </svg>
            </span>
          </div>
        </div>

        <button
          class="h-10 whitespace-nowrap rounded-md border px-3 py-2 text-xs sm:text-sm font-medium"
          :class="view === 'online' ? 'border-blue-700 bg-blue-600 text-white' : 'border-slate-300 bg-slate-100 text-slate-900'"
          @click="(view = view === 'online' ? 'all' : 'online'); refresh()"
        >
          {{ view === 'online' ? 'Online only' : 'All' }}
        </button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-xs sm:text-sm">
        <thead>
          <tr class="border-b border-gray-200 text-left">
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700">ID</th>
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700">Email</th>
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700 hidden sm:table-cell">Role</th>
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700">Status</th>
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700 hidden lg:table-cell">Last Active</th>
            <th class="px-2 py-2 sm:px-4 sm:py-3 font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id" class="border-b border-gray-100 hover:bg-gray-50 text-xs sm:text-sm">
            <td class="px-2 py-2 sm:px-4 sm:py-3 text-gray-700">{{ u.id }}</td>
            <td class="px-2 py-2 sm:px-4 sm:py-3 font-medium text-gray-900 overflow-auto">{{ u.email }}</td>
            <td class="px-2 py-2 sm:px-4 sm:py-3 text-gray-700 capitalize hidden sm:table-cell">{{ u.role }}</td>
            <td class="px-2 py-2 sm:px-4 sm:py-3">
              <div class="flex items-center gap-1 sm:gap-2">
                <span
                  class="h-2 w-2 sm:h-3 sm:w-3 rounded-full"
                  :class="isOnline(u) ? 'bg-green-500' : 'bg-red-500'"
                ></span>
                <span class="font-medium hidden sm:inline" :class="isOnline(u) ? 'text-green-700' : 'text-red-700'">
                  {{ isOnline(u) ? 'Online' : 'Offline' }}
                </span>
              </div>
            </td>
            <td class="px-2 py-2 sm:px-4 sm:py-3 text-gray-700 hidden lg:table-cell text-xs">{{ u.last_active ? new Date(u.last_active).toLocaleString() : '-' }}</td>
            <td class="px-2 py-3 sm:px-4">
              <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-2">
                <button
                  v-if="!u.is_banned"
                  class="rounded bg-red-600 px-2 py-1 text-xs sm:text-sm text-white whitespace-nowrap"
                  @click="banUser(u.id)"
                >
                  Ban
                </button>
                <button
                  v-else
                  class="rounded bg-green-600 px-2 py-1 text-xs sm:text-sm text-white whitespace-nowrap"
                  @click="unbanUser(u.id)"
                >
                  Unban
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-sm text-gray-500">No users found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
</style>
